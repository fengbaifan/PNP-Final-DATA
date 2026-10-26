from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROC = ROOT / "03-processing/patrons-and-painters-full-book-s2/process"
TABLES = ROOT / "04-knowledge/tables"
DATE = "2026-10-26"
ANCHOR = "s3-s4-s5-s6-chp17-p379-p381-manfrin-sources-20261026"
TASK = "patrons-and-painters-full-book-s2"
SOURCE_ID = "haskell-1980-rev-ed"
CH17I = "02-sources/02-Markdown/17_CHP-17_intro.md"
CH17 = "02-sources/02-Markdown/17_CHP-17_sec_i.md"
BIB = "02-sources/02-Markdown/21_CHP-21Bibliography.md"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PROC))
import register_s4_s5_s6_archive_citations_20261020 as card
from scripts import build_field_facts as facts

card.TASK = TASK
card.DATE = DATE
card.ANCHOR = ANCHOR
card.BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)


def src(location, summary, source_file, span, quote, link):
    return {
        "location": location,
        "summary": summary,
        "source_file": source_file,
        "span": span,
        "quotes": [quote],
        "link": link,
    }


SPECS = [
    {
        "candidate": "cand-8332", "group": "archive-group-59d4fac61f33",
        "ku": "units/archives/della-letteratura-veneziana-moschini-1806",
        "path": "04-knowledge/units/archives/della-letteratura-veneziana-moschini-1806.md",
        "zh": "莫斯基尼《十八世纪至今的威尼斯文学》", "en": "Della letteratura veneziana nel secolo XVIII fino a’ nostri giorni (1806)",
        "sub": "book",
        "sources": [
            src("第17章印刷页379注1，L8；PDF物理页1。", "Haskell cites G. A. Meschini in S0 OCR as the author of the only general Manfrin account, vol. II, p. 107. The print image reads Moschini; the cited book was not consulted.", CH17I, "L8; printed p.379 n.1; PDF physical p.1", "The only general account of him and his gallery is given by G. A. Meschini, 1806, II, p. 107.", "[第17章p.379注1](../../../02-sources/02-Markdown/17_CHP-17_intro.md#L8)"),
            src("第21章书目印刷页431，L849–850。", "The bibliography lists a four-volume Venice 1806 work. S0 OCR reads Meschini; the page image reads Moschini. The publication was not independently consulted.", BIB, "L849–850; printed p.431", "Meschini, G. A.: Della letteratura veneziana nel secolo XVIII fino a’ nostri giorni, 4 vols.,", "[第21章p.431书目](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md#L849)"),
        ],
        "fields": [
            ("文献类型", "图书", "S2；第21章书目，印刷页431"),
            ("原题名", "Della letteratura veneziana nel secolo XVIII fino a’ nostri giorni", "S2；第21章书目，印刷页431，L849–850；页图校读Meschini为Moschini"),
            ("书目责任者形式", "G. A. Moschini（按印本页图；S0 OCR作Meschini）", "S1–S2；第17章p.379注1；第21章p.431书目"),
            ("卷数", "4卷", "S2；第21章书目，印刷页431，L849–850"),
            ("出版地", "Venezia", "S2；第21章书目，印刷页431，L850"),
            ("出版年", "1806", "S2；第21章书目，印刷页431，L849–850"),
            ("Haskell所引卷页", "第II卷，第107页；第17章p.379注1、p.380注4、p.381注1", "S1；第17章印刷页379、380、381"),
        ],
        "zhdesc": "本卡登记Haskell第21章书目所列1806年四卷本。p.379注1与p.381注1引第II卷第107页，p.380注4亦引同一卷页并转录对Manfrin画廊的描述。书名与责任者的印本形式据页图校读；原书及被引页未独立查阅。",
        "endesc": "This unit records the four-volume 1806 work listed in Haskell’s chapter 21 bibliography. Chapters 17, notes 1 and 4 on pp. 379–380 and note 1 on p. 381 cite volume II, p. 107; note 4 quotes a description of Manfrin’s gallery. The printed name form is retained from the page image. Neither the book nor the cited page was independently consulted.",
    },
    {
        "candidate": "cand-10682", "group": "archive-group-0f7c84cf9d11",
        "ku": "units/archives/sonetti-xvi-satire-contro-manfrin-correr-2947-18",
        "path": "04-knowledge/units/archives/sonetti-xvi-satire-contro-manfrin-correr-2947-18.md",
        "zh": "反对曼弗林的讽刺诗手稿", "en": "Sonetti XVI, ossiano Satire contro il Manfrin manuscript",
        "sub": "manuscript",
        "sources": [src("第17章印刷页379注2，L9；PDF物理页1。", "Haskell cites a manuscript by title and Correr shelfmark. The scan confirms the title punctuation and printed note number; the manuscript was not consulted.", CH17I, "L9; printed p.379 n.2; PDF physical p.1", "Biblioteca Correr, Venice—Cod. Cicogna 2947/18: Sonetti XVIossiano Satire contro il Manfrin, Impressane di Tabacchi.", "[第17章p.379注2](../../../02-sources/02-Markdown/17_CHP-17_intro.md#L9)")],
        "fields": [
            ("文献类型", "手稿（据Haskell脚注著录）", "S1；第17章印刷页379注2"),
            ("题名（印本页图校读）", "Sonetti XVI, ossiano Satire contro il Manfrin, Impressario di Tabacchi", "S1；第17章印刷页379注2；S0 OCR拼写与空格依页图校读"),
            ("书内档号", "Cod. Cicogna 2947/18", "S1；第17章印刷页379注2"),
            ("书内所报保管机构", "Biblioteca Correr, Venice", "S1；第17章印刷页379注2；现行located_at关系语义待拆分"),
            ("书内引用对象", "反对Manfrin的讽刺诗；手稿未查阅", "S1；第17章印刷页379注2"),
        ],
        "zhdesc": "本卡登记Haskell第17章注2所引、题名为反对Manfrin的讽刺诗手稿及其书内档号。题名空格和Impressario拼写据印本页图校读；手稿与当前馆藏目录均未查阅。",
        "endesc": "This unit records the manuscript of satirical sonnets against Manfrin cited in Haskell’s chapter 17, note 2, with its printed shelfmark. Spacing and the reading Impressario follow the page image. Neither the manuscript nor a current catalog record was consulted.",
    },
    {
        "candidate": "cand-10684", "group": "archive-group-39b63d8c65b3",
        "ku": "units/archives/inquisitori-register-538-p43-1770-01-29",
        "path": "04-knowledge/units/archives/inquisitori-register-538-p43-1770-01-29.md",
        "zh": "國務裁判官檔案第538冊第43頁（1770年1月29日）", "en": "Inquisitori register 538, p. 43 (29 January 1770)",
        "sub": "archival register entry",
        "sources": [src("第17章印刷页379注4，L11；PDF物理页1。", "Haskell gives an Archivio di Stato locator. The scan confirms register 538 where S0 OCR separates the digits; the record was not consulted.", CH17I, "L11; printed p.379 n.4; PDF physical p.1", "Archivio di Stato, Venice—Inquisitori, 53 8, p. 43—29 Genaro 1770.", "[第17章p.379注4](../../../02-sources/02-Markdown/17_CHP-17_intro.md#L11)")],
        "fields": [
            ("文献类型", "档案登记记录（据Haskell定位）", "S1；第17章印刷页379注4"),
            ("档案机构形式", "Archivio di Stato, Venice", "S1；第17章印刷页379注4；机构身份映射至现有KU"),
            ("档案系列形式", "Inquisitori", "S1；第17章印刷页379注4"),
            ("登记册与页码", "register 538, p. 43", "S1；第17章印刷页379注4；页图校读OCR 53 8"),
            ("日期（按原文）", "29 Genaro 1770", "S1；第17章印刷页379注4；档案记录未查阅"),
        ],
        "zhdesc": "本卡登记Haskell第17章注4所列Inquisitori登记册位置：Archivio di Stato, Venice，register 538，第43页，日期照录为29 Genaro 1770。页图支持登记册号码；原档案与当前馆藏目录未查阅。",
        "endesc": "This unit records the Inquisitori register locator cited in Haskell, chapter 17, note 4: Archivio di Stato, Venice, register 538, p. 43, dated 29 Genaro 1770 as printed. The page image supports the register number; neither the archival record nor a current catalog was consulted.",
    },
    {
        "candidate": "cand-10685", "group": "archive-group-45869cfd5312",
        "ku": "units/archives/inquisitori-register-540-p6-1786-06-12",
        "path": "04-knowledge/units/archives/inquisitori-register-540-p6-1786-06-12.md",
        "zh": "國務裁判官檔案第540冊第6頁（1786年6月12日）", "en": "Inquisitori register 540, p. 6 (12 June 1786)",
        "sub": "archival register entry",
        "sources": [src("第17章印刷页379注5，L12；PDF物理页1。", "Haskell’s ibid. continues the Archivio di Stato/Inquisitori locator. The scan confirms printed note 5; the record was not consulted.", CH17I, "L12; printed p.379 n.5; PDF physical p.1", "6 ibid., 540, p. 6—12 Giugno 1786.", "[第17章p.379注5](../../../02-sources/02-Markdown/17_CHP-17_intro.md#L12)")],
        "fields": [
            ("文献类型", "档案登记记录（据Haskell定位）", "S1；第17章印刷页379注5"),
            ("档案机构形式", "Archivio di Stato, Venice（由ibid.承接前注）", "S1；第17章印刷页379注5"),
            ("档案系列形式", "Inquisitori", "S1；第17章印刷页379注4–5"),
            ("登记册与页码", "register 540, p. 6", "S1；第17章印刷页379注5"),
            ("日期（按原文）", "12 Giugno 1786", "S1；第17章印刷页379注5；档案记录未查阅"),
        ],
        "zhdesc": "本卡登记Haskell第17章注5所列Inquisitori登记册位置；ibid.承接注4的Archivio di Stato, Venice。书内给出register 540，第6页，日期为12 Giugno 1786。原档案与当前馆藏目录未查阅。",
        "endesc": "This unit records the Inquisitori register locator cited in Haskell, chapter 17, note 5; ibid. continues the Archivio di Stato, Venice reference in note 4. The cited locator is register 540, p. 6, dated 12 Giugno 1786. Neither the archival record nor a current catalog was consulted.",
    },
    {
        "candidate": "cand-10687", "group": "archive-group-0a001fb5d548",
        "ku": "units/archives/curiosita-veneziane-tassini-fourth-edition-1887",
        "path": "04-knowledge/units/archives/curiosita-veneziane-tassini-fourth-edition-1887.md",
        "zh": "塔西尼《威尼斯趣闻》第四版（1887）", "en": "Curiosità Veneziane, fourth edition (1887)",
        "sub": "book",
        "sources": [src("第17章印刷页379注6，L13；PDF物理页1。", "Haskell cites the fourth edition. The surname-only author candidate remains unresolved; the cited book was not consulted.", CH17I, "L13; printed p.379 n.6; PDF physical p.1", "8 Tassini: Curiosità Veneziane, 4th edition 1887.", "[第17章p.379注6](../../../02-sources/02-Markdown/17_CHP-17_intro.md#L13)")],
        "fields": [
            ("文献类型", "图书", "S1；第17章印刷页379注6"),
            ("书名（书内著录）", "Curiosità Veneziane", "S1；第17章印刷页379注6"),
            ("版次", "第四版", "S1；第17章印刷页379注6"),
            ("出版年", "1887", "S1；第17章印刷页379注6"),
            ("责任者形式", "Tassini（仅按姓氏照录；身份未决）", "S1；第17章印刷页379注6"),
        ],
        "zhdesc": "本卡登记Haskell第17章注6所引《Curiosità Veneziane》第四版（1887）。责任者形式仅照录为Tassini；书目项未提供名字，候选人物身份仍未决。被引书未查阅。",
        "endesc": "This unit records the fourth edition (1887) of Curiosità Veneziane cited in Haskell, chapter 17, note 6. The author form is retained as Tassini; the note supplies no given name and the person candidate remains unresolved. The cited book was not consulted.",
    },
]

SAME = {
    "cand-10172": ("units/institutions/archivio-di-stato-di-venezia", "new", "sg3-institution-cand-10172", "The exact repository name in the p.379 note matches the existing same-type Archivio di Stato di Venezia KU."),
    "cand-10680": ("units/persons/giannantonio-moschini", "undecided", "", "The p.379 scan reads G. A. Moschini; the same source form is tied to the 1806 four-volume title in the p.431 bibliography and matches the existing Treccani-supported Giannantonio Moschini identity. Initials remain the source form."),
    "cand-10681": ("units/archives/della-letteratura-veneziana-moschini-1806", "new", "archive-group-d0625ba01f90", "The p.379 citation gives 1806, vol. II, p.107; the p.431 bibliography identifies the same four-volume 1806 title. This is the same publication as cand-8332."),
    "cand-10700": ("units/archives/della-letteratura-veneziana-moschini-1806", "undecided", "", "The p.381 scan reads Moschini, 1806, vol. II, p.107; this is the same locator and publication as cand-8332. The p.380 spelling difference was OCR, not a printed-source conflict."),
    "cand-9448": ("units/institutions/biblioteca-marciana", "new", "sg3-institution-cand-9448", "Biblioteca Marciana is the same named repository as the existing same-type institutional KU; correct the prior new decision that had already pointed to that KU."),
}

TABLE_NAMES = ["entity-candidates.csv", "alignment.csv", "ku-manifest.csv", "relations.csv"]


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def csv_bytes(path: Path, fields, rows):
    import io
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    data = out.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" if path.read_bytes().startswith(b"\xef\xbb\xbf") else b"") + data


def updated_pamphlet(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig")
    match = re.match(r"\A(?:\ufeff)?---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    assert match, "pamphlet card frontmatter missing"
    import yaml
    fm = yaml.safe_load(match.group(1))
    fm["updated"] = DATE
    fm["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
    source = fm["sources"][0]
    source["location"] = "第17章印刷页379注3，L10；PDF物理页1。"
    source["sentence_summary"] = "Haskell cites a 1797 pamphlet with the locator Biblioteca Marciana 183.C.89, p.321. The page image confirms printed note 3 and reads imparziale where S0 OCR has impacciale; the pamphlet and catalog were not consulted."
    source["evidence_ref"]["source_span"] = "lines L10; printed p.379 n.3; PDF physical p.1; p.321 is the pamphlet locator"
    yaml_front = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000).rstrip()
    body = text[match.end():]
    replacements = [
        ("第十七章注8", "第十七章印刷页379注3"),
        ("Chapter 17 note 8", "Chapter 17, p.379 note 3"),
        ("（OCR L10；印刷页未登记）", "（L10；印刷页379注3；PDF物理页1）"),
        ("原题（按 OCR 转录）", "原题名（印本页图校读；S0 OCR作 impacciale）"),
        ("Risposta alla lettera apologetica impacciale per il Cittadino Gerolamo Manfrin", "Risposta alla lettera apologetica imparziale per il Cittadino Gerolamo Manfrin"),
        ("canonical_name 记作 imparziale，而第十七章 OCR 转录为 impacciale。未对照扫描原页", "候选 canonical_name 记作 imparziale；印本页图读作 imparziale，S0 OCR 为 impacciale"),
        ("The S2 candidate canonical_name records imparziale, while the Chapter 17 OCR transcription reads impacciale. The scan has not been checked", "The candidate canonical_name and printed page image read imparziale; S0 OCR reads impacciale"),
        ("脚注8的 Haskell 印刷页未在当前 S2 定位中登记；其中 p.321 是小册子引用页，不能当作 Haskell 的印刷页。", "Haskell脚注位于印刷页379注3；p.321是书中所列小册子页码，不是Haskell页码。"),
        ("The Haskell printed page for note 8 is not registered in the current S2 locator; p. 321 is the cited pamphlet page, not Haskell’s printed page.", "Haskell’s note is on printed p.379 n.3; p.321 is the cited pamphlet page, not Haskell’s page."),
        ("当前没有正式关系。正文中的导航与线索不自动形成关系边。", "正式的Haskell引文边由relations.csv渲染；小册子的馆藏定位仍待证，因为located_at的语义边界尚待拆分。"),
        ("S2 的馆藏定位关系候选留待 S6；机构身份入口为[Biblioteca Marciana]", "S2馆藏定位候选留待S6；机构身份入口为[Biblioteca Marciana]"),
    ]
    for old, new in replacements:
        assert old in body, f"pamphlet replacement anchor missing: {old[:70]}"
        body = body.replace(old, new)
    # Every structured fact row gains an explicit source marker for the existing Haskell source.
    lines = body.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("|") and not re.match(r"\|\s*[-: ]+\|", line):
            cells = line.strip().strip("|").split("|")
            if len(cells) == 3 and cells[0].strip() != "字段" and "S1" not in cells[-1]:
                cells[-1] = cells[-1].rstrip() + "；S1"
                lines[i] = "| " + " | ".join(cell.strip() for cell in cells) + " |"
    body = "\n".join(lines)
    return "---\n" + yaml_front + "\n---\n" + body


def new_citation_statement(parent: dict, statement_id: str, target: str, claim: str, note: str) -> dict:
    row = copy.deepcopy(parent)
    row["statement_id"] = statement_id
    row["subject_candidate_id"] = "cand-2962"
    row["object_candidate_id"] = target
    row["predicate"] = "cites"
    q = row["qualifiers"]
    q["claim"] = claim
    q["speaker"] = "Haskell"
    q["text_layer"] = "bibliographic citation"
    q["qualification"] = "This records Haskell's citation only; the cited item and cited page were not independently consulted."
    q["mentioned_candidate_ids"] = list(dict.fromkeys(["cand-2962", target] + [x for x in q.get("mentioned_candidate_ids", []) if x not in {"cand-2962", target}]))
    q["relation_candidate"] = True
    q["relation_candidate_note"] = note
    return row


def planned_statement_bytes(path: Path, by_id: dict[str, dict], new_rows: list[dict]):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    payload = raw[3:] if bom else raw
    lines = payload.splitlines(keepends=True)
    out: list[bytes] = []
    seen = set()
    newline = b"\r\n" if any(line.endswith(b"\r\n") for line in lines[:1]) else b"\n"
    parents = {
        "st-chp17-pi-note1-meschini-account": [new_rows[0]],
        "st-chp17-pi-note2-correr-manuscript-locator": [new_rows[1]],
        "st-chp17-pi-note3-pamphlet-locator": [new_rows[2]],
        "st-chp17-pi-note4-1770-archive-locator": [new_rows[3]],
        "st-chp17-pi-note5-1786-archive-locator": [new_rows[4]],
        "st-chp17-pi-note6-tassini-locator": [new_rows[5]],
    }
    for line in lines:
        content = line.rstrip(b"\r\n")
        row = json.loads(content.decode("utf-8"))
        sid = row["statement_id"]
        if sid in by_id:
            assert sid not in seen, sid
            replacement = copy.deepcopy(by_id[sid])
            seen.add(sid)
            out.append(json.dumps(replacement, ensure_ascii=False).encode("utf-8") + newline)
        else:
            out.append(line)
        for added in parents.get(sid, []):
            out.append(json.dumps(added, ensure_ascii=False).encode("utf-8") + newline)
    assert seen == set(by_id), set(by_id) - seen
    return (b"\xef\xbb\xbf" if bom else b"") + b"".join(out)


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    proc_path = PROC / "knowledge.md"
    stages_path = PROC / "stages.md"
    result_path = ROOT / "04-knowledge/results/patrons-and-painters-full-book-s2.md"
    paths = {name: TABLES / name for name in TABLE_NAMES}
    paths.update({
        "accepted": ROOT / "04-knowledge/accepted.yml",
        "statements": TABLES / "book-statements.jsonl",
        "enrichment": TABLES / "enrichment.jsonl",
        "sources": TABLES / "sources.csv",
        "process": proc_path,
        "stages": stages_path,
    })
    cfields, candidates = read_csv(paths["entity-candidates.csv"])
    afields, alignments = read_csv(paths["alignment.csv"])
    mfields, manifest = read_csv(paths["ku-manifest.csv"])
    rfields, relations = read_csv(paths["relations.csv"])
    cby = {r["candidate_id"]: r for r in candidates}
    primary = {r["candidate_id"]: r for r in alignments if r.get("candidate_id") and not r.get("external_source")}
    assert all(cid in cby and cid in primary for cid in SAME)
    for cid, (ku, old_decision, old_group, rationale) in SAME.items():
        assert primary[cid]["decision"] == old_decision, (cid, primary[cid]["decision"], old_decision)
        assert primary[cid]["ku_id"] in {"", ku}, (cid, primary[cid]["ku_id"])
        if old_group:
            assert f"group={old_group}" in primary[cid]["resolution_note"]
        assert ku in {r["ku_id"] for r in manifest} or any(s["ku"] == ku for s in SPECS)
    for s in SPECS:
        assert cby[s["candidate"]]["suggested_type"] == "archive"
        a = primary[s["candidate"]]
        assert a["decision"] == "new" and not a["ku_id"]
        assert f"group={s['group']}" in a["resolution_note"]
        assert s["ku"] not in {r["ku_id"] for r in manifest}
        assert not (ROOT / s["path"]).exists()
    assert primary["cand-1513"]["decision"] == "undecided"
    assert primary["cand-10686"]["decision"] == "undecided"
    assert primary["cand-10701"]["decision"] == "undecided"
    assert "units/archives/patrons-and-painters" in {r["ku_id"] for r in manifest}
    assert "units/archives/epistolario-moschini" in {r["ku_id"] for r in manifest}
    assert "units/archives/manfrin-edwards-letter-1793-12-03" in {r["ku_id"] for r in manifest}
    relation_ids = [int(r["relation_id"].split("-")[1]) for r in relations]
    assert max(relation_ids) == 2301
    assert any(r["relation_id"] == "rel-1593" and r["subject_ku_id"] == "units/archives/manfrin-edwards-letter-1793-12-03" and r["object_ku_id"] == "units/archives/epistolario-moschini" and r["predicate"] == "part_of" for r in relations)
    process = paths["process"].read_text(encoding="utf-8-sig")
    stages = paths["stages"].read_text(encoding="utf-8-sig")
    assert ANCHOR not in process and ANCHOR not in stages
    # The source statements live in book-statements.jsonl; this process section
    # is deliberately appended only after the statement preflight succeeds.
    statement_rows = [json.loads(line) for line in paths["statements"].read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    by_id = {r["statement_id"]: r for r in statement_rows}
    expected_parent_ids = [
        "st-chp17-pi-note1-meschini-account", "st-chp17-pi-note2-correr-manuscript-locator",
        "st-chp17-pi-note3-pamphlet-locator", "st-chp17-pi-note4-1770-archive-locator",
        "st-chp17-pi-note5-1786-archive-locator", "st-chp17-pi-note6-tassini-locator",
        "st-chp17-p380-note4-meschini-gallery-description", "st-chp17-p380-note6-edwards-letter-source",
        "st-chp17-p381-note1-moschini-1806", "st-chp17-p381-note1-moschini-1810",
    ]
    assert all(sid in by_id and by_id[sid]["qualifiers"].get("relation_candidate") for sid in expected_parent_ids)
    new_statement_ids = [
        "st-chp17-pi-note1-cites-moschini-1806", "st-chp17-pi-note2-cites-correr-sonetti",
        "st-chp17-pi-note3-cites-manfrin-pamphlet", "st-chp17-pi-note4-cites-inquisitori-538",
        "st-chp17-pi-note5-cites-inquisitori-540", "st-chp17-pi-note6-cites-tassini-1887",
    ]
    assert not (set(new_statement_ids) & set(by_id))
    cite_targets = ["cand-10681", "cand-10682", "cand-10683", "cand-10684", "cand-10685", "cand-10687"]
    citation_claims = [
        "Haskell cites G. A. Moschini, 1806, volume II, p.107 as the only general account of Manfrin and his gallery.",
        "Haskell cites the Sonetti XVI manuscript, Cod. Cicogna 2947/18, at Biblioteca Correr.",
        "Haskell cites the 1797 pamphlet Risposta alla lettera apologetica imparziale, with the printed locator 183.C.89, p.321.",
        "Haskell cites Archivio di Stato, Venice, Inquisitori register 538, p.43.",
        "Haskell's ibid. cites Inquisitori register 540, p.6.",
        "Haskell cites the fourth edition of Curiosità Veneziane (1887).",
    ]
    citation_notes = [
        "Haskell's p.379 note 1 gives the volume/page citation; the printed author spelling is Moschini.",
        "Haskell's p.379 note 2 cites the titled manuscript and shelfmark; manuscript contents were not consulted.",
        "Haskell's p.379 note 3 cites the pamphlet; p.321 is its locator, not Haskell's page.",
        "Haskell's p.379 note 4 cites this record; its physical repository locator remains a separate pending candidate.",
        "Haskell's p.379 note 5 cites this record; its physical repository locator remains a separate pending candidate.",
        "Haskell's p.379 note 6 cites this edition; the surname-only author identity remains unresolved.",
    ]
    new_rows = [new_citation_statement(by_id[expected_parent_ids[i]], new_statement_ids[i], cite_targets[i], citation_claims[i], citation_notes[i]) for i in range(6)]
    planned_by_id = copy.deepcopy(by_id)
    for cid in SAME:
        row = copy.deepcopy(primary[cid])
        target, old_decision, old_group, rationale = SAME[cid]
        old_note = row["resolution_note"]
        row["decision"] = "same"
        row["ku_id"] = target
        row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
        row["resolution_note"] = old_note + f" prior_decision={old_decision}; prior_group={old_group or 'unresolved'}; revised_decision=same; target_ku_id={target}. {rationale}"
        primary[cid].update(row)
    for cid, proper_name, detail in [
        ("cand-10680", "G. A. Moschini (author named in Haskell's Manfrin note)", "The source supplies initials and surname only; no fuller name is inferred from this mention. The p.379 print image reads Moschini while S0 OCR reads Meschini."),
        ("cand-10681", "G. A. Moschini, 1806, volume II, p.107 (general Manfrin account cited by Haskell)", "The p.379, p.380 and p.381 print images read Moschini, 1806, volume II, p.107. The cited publication was not independently consulted."),
    ]:
        cby[cid]["canonical_name"] = proper_name
        cby[cid]["detail"] = detail
    planned_manifest = list(manifest)
    for s in SPECS:
        a = primary[s["candidate"]]
        a["ku_id"] = s["ku"]
        a["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
        a["resolution_note"] += f" S4 registration: {s['group']} maps to {s['ku']}; the KU records Haskell's cited item only."
        planned_manifest.append({"ku_id": s["ku"], "type": "archive", "canonical_name": s["zh"], "name_en": s["en"], "source_task": TASK, "card_path": s["path"]})
    alignment_bytes = csv_bytes(paths["alignment.csv"], afields, alignments)
    candidate_bytes = csv_bytes(paths["entity-candidates.csv"], cfields, candidates)
    manifest_bytes = csv_bytes(paths["ku-manifest.csv"], mfields, planned_manifest)
    accepted = paths["accepted"].read_text(encoding="utf-8-sig")
    accepted_new = card.insert_accepted_paths(accepted, [s["path"] for s in SPECS])
    card_texts = {ROOT / s["path"]: card.make_archive_card({
        "candidate": s["candidate"], "group": s["group"], "ku_id": s["ku"], "type": "archive",
        "sub_type": s["sub"], "name_zh": s["zh"], "name_en": s["en"], "card_path": s["path"],
        "sources": s["sources"], "fields": s["fields"], "paragraph_zh": s["zhdesc"], "paragraph_en": s["endesc"],
    }) for s in SPECS}
    pamphlet_path = ROOT / "04-knowledge/units/archives/manfrin-pamphlet-risposta-1797.md"
    card_texts[pamphlet_path] = updated_pamphlet(pamphlet_path)
    planned_rels = list(relations)
    start = max(relation_ids) + 1
    relation_specs = [
        ("units/archives/della-letteratura-veneziana-moschini-1806", "units/persons/giannantonio-moschini", "authored_by", "書目責任者", "Haskell第17章p.379注1把G. A. Moschini列为Manfrin及其画廊唯一通论的作者；只记录来源归属，不表示已查阅原书。", CH17I, "printed p.379 n.1, L8; statement=st-chp17-pi-note1-meschini-account", "S2 candidate: st-chp17-pi-note1-meschini-account; cited title and p.431 bibliography cross-check the same 1806 publication."),
        ("units/archives/patrons-and-painters", "units/archives/della-letteratura-veneziana-moschini-1806", "cites", "书内引文", "Haskell第17章p.379注1、p.380注4及p.381注1引Moschini 1806年著作第II卷第107页；被引页未独立查阅。", CH17I, "printed p.379 n.1, L8; statements=st-chp17-pi-note1-cites-moschini-1806, st-chp17-p380-note4-meschini-gallery-description, st-chp17-p381-note1-moschini-1806", "S2 citation statement: st-chp17-pi-note1-cites-moschini-1806; same citation is repeated in p.380 n.4 and p.381 n.1."),
        ("units/archives/patrons-and-painters", "units/archives/sonetti-xvi-satire-contro-manfrin-correr-2947-18", "cites", "书内引文", "Haskell第17章p.379注2引用题为Sonetti XVI的手稿并给出Cod. Cicogna 2947/18定位；手稿未查阅。", CH17I, "printed p.379 n.2, L9; statement=st-chp17-pi-note2-cites-correr-sonetti", "S2 citation statement: st-chp17-pi-note2-cites-correr-sonetti."),
        ("units/archives/patrons-and-painters", "units/archives/manfrin-pamphlet-risposta-1797", "cites", "书内引文", "Haskell第17章p.379注3引用1797年小册子；p.321为小册子页码。", CH17I, "printed p.379 n.3, L10; statement=st-chp17-pi-note3-cites-manfrin-pamphlet", "S2 citation statement: st-chp17-pi-note3-cites-manfrin-pamphlet. Physical repository location is separately pending."),
        ("units/archives/patrons-and-painters", "units/archives/inquisitori-register-538-p43-1770-01-29", "cites", "书内引文", "Haskell第17章p.379注4引用register 538, p.43, dated 29 Genaro 1770; the archival record was not consulted.", CH17I, "printed p.379 n.4, L11; statement=st-chp17-pi-note4-cites-inquisitori-538", "S2 citation statement: st-chp17-pi-note4-cites-inquisitori-538. Physical repository location is separately pending."),
        ("units/archives/patrons-and-painters", "units/archives/inquisitori-register-540-p6-1786-06-12", "cites", "书内引文", "Haskell第17章p.379注5引用register 540, p.6, dated 12 Giugno 1786; the archival record was not consulted.", CH17I, "printed p.379 n.5, L12; statement=st-chp17-pi-note5-cites-inquisitori-540", "S2 citation statement: st-chp17-pi-note5-cites-inquisitori-540. Physical repository location is separately pending."),
        ("units/archives/patrons-and-painters", "units/archives/curiosita-veneziane-tassini-fourth-edition-1887", "cites", "书内引文", "Haskell第17章p.379注6引用Curiosità Veneziane第四版（1887）；被引书未查阅。", CH17I, "printed p.379 n.6, L13; statement=st-chp17-pi-note6-cites-tassini-1887", "S2 citation statement: st-chp17-pi-note6-cites-tassini-1887. The surname-only author identity remains undecided."),
    ]
    for i, (subject, obj, predicate, role, scope, source_file, span, note) in enumerate(relation_specs):
        rid = f"rel-{start+i:04d}"
        key = (subject, predicate, obj, "", role, scope)
        assert not any((r["subject_ku_id"], r["predicate"], r["object_ku_id"], r["time"], r["role"], r["scope"]) == key for r in relations), key
        planned_rels.append({"relation_id": rid, "subject_ku_id": subject, "object_ku_id": obj, "predicate": predicate, "time": "", "role": role, "scope": scope, "origin": "book", "status": "formal", "source_id": SOURCE_ID, "source_span": span, "source_file": source_file, "note": note})
    relation_bytes = csv_bytes(paths["relations.csv"], rfields, planned_rels)
    parent_map = {
        "st-chp17-pi-note1-meschini-account": ("st-chp17-pi-note1-cites-moschini-1806", "cand-10681", "Haskell cites G. A. Moschini, 1806, volume II, p.107 as the only general account of Manfrin and his gallery.", "Haskell's p.379 note 1 gives the volume/page citation; the printed author spelling is Moschini."),
        "st-chp17-pi-note2-correr-manuscript-locator": ("st-chp17-pi-note2-cites-correr-sonetti", "cand-10682", "Haskell cites the Sonetti XVI manuscript, Cod. Cicogna 2947/18, at Biblioteca Correr.", "Haskell's p.379 note 2 cites the titled manuscript and shelfmark; the manuscript was not consulted."),
        "st-chp17-pi-note3-pamphlet-locator": ("st-chp17-pi-note3-cites-manfrin-pamphlet", "cand-10683", "Haskell cites the 1797 pamphlet Risposta alla lettera apologetica imparziale, with the printed locator 183.C.89, p.321.", "Haskell's p.379 note 3 cites the pamphlet; p.321 is its locator, not Haskell's page."),
        "st-chp17-pi-note4-1770-archive-locator": ("st-chp17-pi-note4-cites-inquisitori-538", "cand-10684", "Haskell cites Archivio di Stato, Venice, Inquisitori register 538, p.43.", "Haskell's p.379 note 4 cites this record; its physical repository locator remains a separate pending candidate."),
        "st-chp17-pi-note5-1786-archive-locator": ("st-chp17-pi-note5-cites-inquisitori-540", "cand-10685", "Haskell's ibid. cites Inquisitori register 540, p.6.", "Haskell's p.379 note 5 cites this record; its physical repository locator remains a separate pending candidate."),
        "st-chp17-pi-note6-tassini-locator": ("st-chp17-pi-note6-cites-tassini-1887", "cand-10687", "Haskell cites the fourth edition of Curiosità Veneziane (1887).", "Haskell's p.379 note 6 cites this edition; the surname-only author identity remains unresolved."),
    }
    new_statements = []
    for parent_id, (sid, target, claim, note) in parent_map.items():
        new_statements.append(new_citation_statement(by_id[parent_id], sid, target, claim, note))
    planned_statement_rows = copy.deepcopy(by_id)
    for sid, row in planned_statement_rows.items():
        if sid == "st-chp17-pi-note1-meschini-account":
            q = row["qualifiers"]
            q["claim"] = "Haskell identifies G. A. Moschini's 1806 volume II, page 107 as the only general account of Manfrin and his gallery."
            q["speaker"] = "Haskell"
            q["qualification"] = "The cited work and page were not independently consulted; the initials remain unexpanded in this source statement. The physical p.379 image reads Moschini; S0 OCR reads Meschini."
            corrections = q.setdefault("ocr_corrections", [])
            if not any(c.get("source_line") == 8 and c.get("ocr") == "Meschini" for c in corrections):
                corrections.append({"source_file": CH17I, "source_line": 8, "ocr": "Meschini", "print": "Moschini", "basis": "CHP-17.pdf physical page 1, printed page 379."})
        elif sid == "st-chp17-pi-note2-correr-manuscript-locator":
            row["subject_candidate_id"], row["object_candidate_id"], row["predicate"] = "cand-10682", "cand-8262", "located_at"
            q = row["qualifiers"]
            q["claim"] = "Haskell locates the cited satirical sonnets at Biblioteca Correr, Cod. Cicogna 2947/18."
            q["qualification"] = "The manuscript was not consulted; the physical holding relation remains pending because located_at is marked needs_split. The scan reads Sonetti XVI, ossiano and Impressario; S0 OCR has spacing/spelling errors."
            q["printed_page"] = 379
            q["ocr_corrections"] = [
                {"source_file": CH17I, "source_line": 9, "ocr": "Sonetti XVIossiano", "print": "Sonetti XVI, ossiano", "basis": "CHP-17.pdf physical page 1, printed page 379."},
                {"source_file": CH17I, "source_line": 9, "ocr": "Impressane", "print": "Impressario", "basis": "CHP-17.pdf physical page 1, printed page 379."},
            ]
        elif sid == "st-chp17-pi-note3-pamphlet-locator":
            row["predicate"] = "located_at"
            q = row["qualifiers"]
            q["claim"] = "Haskell cites a 1797 pamphlet against Gerolamo Manfrin at Biblioteca Marciana shelfmark 183.C.89, p.321."
            q["qualification"] = "The pamphlet and repository record were not consulted. The physical p.379 image reads imparziale and note 3; S0 OCR reads impacciale and note 8. The location relation remains pending because located_at is marked needs_split."
            q["printed_page"] = 379
            q["ocr_corrections"] = [
                {"source_file": CH17I, "source_line": 10, "ocr": "impacciale", "print": "imparziale", "basis": "CHP-17.pdf physical page 1, printed page 379."},
                {"source_file": CH17I, "source_line": 10, "ocr": "8", "print": "3", "basis": "CHP-17.pdf physical page 1, printed page 379."},
            ]
        elif sid == "st-chp17-pi-note4-1770-archive-locator":
            row["subject_candidate_id"], row["object_candidate_id"], row["predicate"] = "cand-10684", "cand-10172", "located_at"
            q = row["qualifiers"]
            q["claim"] = "Haskell cites Archivio di Stato, Venice, Inquisitori register 538, p.43, dated 29 Genaro 1770."
            q["qualification"] = "The archival record was not consulted; the scan confirms register 538 where S0 OCR has 53 8. Physical repository location remains pending because located_at is marked needs_split."
            q["printed_page"] = 379
        elif sid == "st-chp17-pi-note5-1786-archive-locator":
            row["subject_candidate_id"], row["object_candidate_id"], row["predicate"] = "cand-10685", "cand-10172", "located_at"
            q = row["qualifiers"]
            q["claim"] = "Haskell's ibid. cites Archivio di Stato, Venice, Inquisitori register 540, p.6, dated 12 Giugno 1786."
            q["qualification"] = "The record was not consulted. The physical page shows printed note 5 where S0 OCR shows note 6. Physical repository location remains pending because located_at is marked needs_split."
            q["printed_page"] = 379
            q["ocr_corrections"] = [{"source_file": CH17I, "source_line": 12, "ocr": "6", "print": "5", "basis": "CHP-17.pdf physical page 1, printed page 379."}]
        elif sid == "st-chp17-pi-note6-tassini-locator":
            row["subject_candidate_id"], row["object_candidate_id"], row["predicate"] = "cand-10687", "cand-10686", "authored_by"
            q = row["qualifiers"]
            q["claim"] = "Haskell cites the fourth edition of Curiosità Veneziane (1887) under the surname form Tassini."
            q["qualification"] = "The book was not consulted; the surname-only person candidate remains S3 undecided, so no authorship edge is formalized. The page image shows printed note 6 where S0 OCR shows note 8."
            q["printed_page"] = 379
            q["ocr_corrections"] = [{"source_file": CH17I, "source_line": 13, "ocr": "8", "print": "6", "basis": "CHP-17.pdf physical page 1, printed page 379."}]
        elif sid == "st-chp17-p380-note4-meschini-gallery-description":
            row["subject_candidate_id"], row["object_candidate_id"], row["predicate"] = "cand-10681", "cand-1513", "has_subject"
            q = row["qualifiers"]
            q["claim"] = "Haskell quotes G. A. Moschini describing Manfrin's multi-room gallery and its historical survey across painters, periods and schools."
            q["speaker"] = "G. A. Moschini, as quoted by Haskell"
            q["qualification"] = "The cited book was not independently consulted. The physical p.380 image reads Moschini; S0 OCR reads Meschini. The gallery/collection candidate cand-1513 remains untyped, so this subject relation is pending."
            corrections = q.setdefault("ocr_corrections", [])
            if not any(c.get("source_line") == 29 and c.get("ocr") == "Meschini" for c in corrections):
                corrections.append({"source_file": CH17, "source_line": 29, "ocr": "Meschini", "print": "Moschini", "basis": "CHP-17.pdf physical page 2, printed page 380."})
        elif sid == "st-chp17-p380-note6-edwards-letter-source":
            row["subject_candidate_id"], row["object_candidate_id"], row["predicate"] = "cand-1515", "cand-10605", "part_of"
            q = row["qualifiers"]
            q["claim"] = "Haskell identifies the Manfrin-Edwards letter printed in Appendix 7 as a document in Biblioteca Correr's Epistolario Moschini."
            q["qualification"] = "Appendix 7 identifies the same 3 December 1793 letter and supports reuse of existing formal part_of relation rel-1593. The manuscript and catalog were not consulted."
        elif sid == "st-chp17-p381-note1-moschini-1806":
            row["subject_candidate_id"], row["object_candidate_id"], row["predicate"] = "cand-2962", "cand-10700", "cites"
            q = row["qualifiers"]
            q["claim"] = "Haskell p.381 note 1 cites Moschini, 1806, volume II, p.107 for the Manfrin patronage passage."
            q["qualification"] = "The cited book and page were not independently consulted. The p.380 page image also reads Moschini; the earlier spelling difference was OCR, not a print discrepancy."
            q["mentioned_candidate_ids"] = list(dict.fromkeys(["cand-2962", "cand-1709", "cand-10700"]))
        elif sid == "st-chp17-p381-note1-moschini-1810":
            row["subject_candidate_id"], row["object_candidate_id"], row["predicate"] = "cand-2962", "cand-10701", "cites"
            q = row["qualifiers"]
            q["claim"] = "Haskell p.381 note 1 adds an 1810 citation by the same author, without a title or page."
            q["qualification"] = "The cited item is not identified beyond year and the same-author reference; candidate cand-10701 remains S3 undecided and S6 pending."
            q["mentioned_candidate_ids"] = list(dict.fromkeys(["cand-2962", "cand-1709", "cand-10701"]))
    statement_updates = {
        sid: row for sid, row in planned_statement_rows.items()
        if row != by_id[sid]
    }
    statement_bytes = planned_statement_bytes(paths["statements"], statement_updates, new_statements)
    # Validate generated fields against temporary copies before any write.
    temp_root = None
    import tempfile
    temp_root = tempfile.TemporaryDirectory(prefix="pnp-chp17-manfrin-preview-")
    old_base = facts.BASE
    try:
        facts.BASE = Path(temp_root.name)
        for dest, content in card_texts.items():
            relative = dest.relative_to(ROOT)
            temp_card = facts.BASE / relative
            temp_card.parent.mkdir(parents=True, exist_ok=True)
            temp_card.write_text(content, encoding="utf-8-sig", newline="\n")
        selected_kus = {s["ku"] for s in SPECS} | {"units/archives/manfrin-pamphlet-risposta-1797"}
        selected = [r for r in planned_manifest if r["ku_id"] in selected_kus]
        field_rows, field_sources, warnings, cards_with_tables = facts.extract_records(selected)
    finally:
        facts.BASE = old_base
        temp_root.cleanup()
    assert not warnings, warnings
    assert cards_with_tables == 6, cards_with_tables
    assert len(field_rows) == 34, len(field_rows)
    assert all(r["evidence_status"] == "source_backed" and r["source_ids"] == [SOURCE_ID] for r in field_rows)
    facts.assign_ids(field_rows, paths["enrichment"])
    old_enrichment = [
        json.loads(line) for line in paths["enrichment"].read_text(encoding="utf-8-sig").splitlines() if line.strip()
    ]
    old_enrichment_by_id = {row.get("enrichment_id", ""): row for row in old_enrichment}
    planned_enrichment_by_id = {row.get("enrichment_id", ""): row for row in field_rows}
    selected_kus = {s["ku"] for s in SPECS} | {"units/archives/manfrin-pamphlet-risposta-1797"}
    planned_enrichment = []
    for old_row in old_enrichment:
        enrichment_id = old_row.get("enrichment_id", "")
        if old_row.get("ku_id") in selected_kus:
            if enrichment_id in planned_enrichment_by_id:
                planned_enrichment.append(planned_enrichment_by_id[enrichment_id])
        else:
            planned_enrichment.append(old_row)
    planned_enrichment.extend(
        row for row in field_rows if row.get("enrichment_id", "") not in old_enrichment_by_id
    )
    new_enrichment_ids = set(planned_enrichment_by_id) - set(old_enrichment_by_id)
    removed_enrichment_ids = {
        enrichment_id for enrichment_id, row in old_enrichment_by_id.items()
        if row.get("ku_id") in selected_kus and enrichment_id not in planned_enrichment_by_id
    }
    assert len(new_enrichment_ids) == 27, sorted(new_enrichment_ids)
    assert not removed_enrichment_ids, sorted(removed_enrichment_ids)
    enrichment_bytes = ("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in planned_enrichment)).encode("utf-8")
    # Correct source-file anchors are checked against the immutable S0 transcription.
    source_intro = (ROOT / CH17I).read_text(encoding="utf-8-sig")
    source_main = (ROOT / CH17).read_text(encoding="utf-8-sig")
    source_bib = (ROOT / BIB).read_text(encoding="utf-8-sig")
    for needle in ["Meschini, 1806, II, p. 107", "Cod. Cicogna 2947/18", "impacciale", "53 8, p. 43", "540, p. 6", "Curiosità Veneziane"]:
        assert needle in source_intro, needle
    assert "Meschini, 1806, II, p. 107:" in source_main
    assert "Meschini, G. A.: Della letteratura veneziana" in source_bib
    # Final bytes are assembled without reserializing unrelated source statements.
    accepted_new = card.insert_accepted_paths(accepted, [s["path"] for s in SPECS])
    writes = {
        paths["entity-candidates.csv"]: candidate_bytes,
        paths["alignment.csv"]: alignment_bytes,
        paths["ku-manifest.csv"]: manifest_bytes,
        paths["relations.csv"]: relation_bytes,
        paths["statements"]: statement_bytes,
        paths["enrichment"]: enrichment_bytes,
        paths["accepted"]: (b"\xef\xbb\xbf" if paths["accepted"].read_bytes().startswith(b"\xef\xbb\xbf") else b"") + accepted_new.encode("utf-8"),
    }
    for dest, content in card_texts.items():
        writes[dest] = content.encode("utf-8-sig")
    process_note = f"""

<a id="{ANCHOR}"></a>

### S3–S6：第17章印刷页379–381 Manfrin引注、来源身份及关系端点（{DATE}）

#### 来源证据与S3跨章身份裁决

复核第17章印刷页379–381（CHP-17.pdf物理页1–3）及第21章印刷页431书目。页图确认p.379注1、p.380注4、p.381注1印作Moschini；OCR的Meschini仅为转录误差。第21章书目OCR同作Meschini，但p.431页图列出G. A. Moschini四卷本 *Della letteratura veneziana nel secolo XVIII fino a’ nostri giorni*，Venezia 1806。原书及其第II卷第107页未查阅。p.379注2印本题名为 *Sonetti XVI, ossiano Satire contro il Manfrin, Impressario di Tabacchi*；注3印本为 *imparziale*、注号3；注4登记册为538；注5、注6的印本注号分别为5、6。

| 候选 | 原决定 | 当前决定与S4去向 | 依据 |
|---|---|---|---|
| cand-10172 | new | same → units/institutions/archivio-di-stato-di-venezia | p.379注4、5的Archivio di Stato, Venice与现有同类型机构KU相同。|
| cand-10680 | undecided | same → units/persons/giannantonio-moschini | p.379页图读G. A. Moschini；跨章姓名、Abate称谓及现有Treccani DBI身份记录支持同一人物；本句仍保留缩写。|
| cand-8332 | new | new → units/archives/della-letteratura-veneziana-moschini-1806 | p.431四卷书目与第17章卷页引注对应。|
| cand-10681 | new，archive-group-d0625ba01f90 | same → units/archives/della-letteratura-veneziana-moschini-1806 | 1806，II卷，p.107，与cand-8332同一出版物；保留原组及其历史裁决。|
| cand-10700 | undecided | same → units/archives/della-letteratura-veneziana-moschini-1806 | p.381印本与p.379、p.380引注为同一书卷页；无印本拼写冲突。|
| cand-10682 | new，archive-group-0f7c84cf9d11 | new → units/archives/sonetti-xvi-satire-contro-manfrin-correr-2947-18 | 独立手稿题名与Cod. Cicogna 2947/18。|
| cand-10684 | new，archive-group-39b63d8c65b3 | new → units/archives/inquisitori-register-538-p43-1770-01-29 | register 538，p.43，29 Genaro 1770。|
| cand-10685 | new，archive-group-45869cfd5312 | new → units/archives/inquisitori-register-540-p6-1786-06-12 | register 540，p.6，12 Giugno 1786；与538册记录分开。|
| cand-10687 | new，archive-group-0a001fb5d548 | new → units/archives/curiosita-veneziane-tassini-fourth-edition-1887 | 第四版1887，与既有第五版1915候选cand-8428保持分开。|
| cand-9448 | new | same → units/institutions/biblioteca-marciana | p.379注3的同名机构已由该候选映射；更正决策与既有KU不一致的问题。|

`cand-10686`（Tassini，仅姓氏）继续undecided；`cand-1513`（Manfrin gallery/collection）继续untyped/undecided；`cand-10701`（Moschini, 1810，无题名或页码）继续undecided。未据此创建作者或馆藏推断。`cand-8262`及`cand-10605`沿用Correr Library与Epistolario Moschini既有KU。

#### S2定位和原子关系修订

保留S0原文和现有`original_quote`；把图像校读作为qualifier记录。修正p.379注1与p.380注4的Meschini→Moschini，p.379注2的题名空格与Impressario、p.379注3的imparziale及注号3、p.379注4的538、p.379注5和注6的注号。修正关系方向：手稿/小册子/档案记录指向书内所报机构；p.380注4为Moschini出版物`has_subject` Manfrin gallery候选；p.380注6为1793书信`part_of` Epistolario Moschini；p.381注1以Haskell书为subject记录对1806书的`cites`，1810未识别文献同样以Haskell书为subject。

新增6条独立citation statement，分别将Haskell书与p.379注1–6各自具名引注相连；不新增mention。全部新增statement及本批修订均不计入S2独立复核分子。书内地点定位candidate保留为独立S2声明，不因新增citation statement而合并。

#### S6逐项裁决

| S2 statement | 决定与去向 |
|---|---|
| st-chp17-pi-note1-meschini-account | formal rel-{start:04d} `authored_by`：1806出版物→Giannantonio Moschini；只表达Haskell的作者归属。|
| st-chp17-pi-note1-cites-moschini-1806 | formal rel-{start+1:04d} `cites`：Haskell→1806出版物。|
| st-chp17-pi-note2-correr-manuscript-locator | pending `located_at`：端点齐全；关系词表将located_at标为needs_split，书内馆藏定位尚无可用的独立谓词。|
| st-chp17-pi-note2-cites-correr-sonetti | formal rel-{start+2:04d} `cites`：Haskell→手稿；不表示已查阅手稿。|
| st-chp17-pi-note3-pamphlet-locator | pending `located_at`：Marciana身份与小册子KU已映射，但档案馆藏定位的谓词语义待拆分。|
| st-chp17-pi-note3-cites-manfrin-pamphlet | formal rel-{start+3:04d} `cites`：Haskell→1797小册子。|
| st-chp17-pi-note4-1770-archive-locator | pending `located_at`：ASV机构与register 538 KU已映射；needs_split阻止把书内档案定位冒充为已定义位置关系。|
| st-chp17-pi-note4-cites-inquisitori-538 | formal rel-{start+4:04d} `cites`：Haskell→register 538记录。|
| st-chp17-pi-note5-1786-archive-locator | pending `located_at`：ASV机构与register 540 KU已映射；needs_split阻止地点关系写回。|
| st-chp17-pi-note5-cites-inquisitori-540 | formal rel-{start+5:04d} `cites`：Haskell→register 540记录。|
| st-chp17-pi-note6-tassini-locator | pending `authored_by`：书已登记；姓氏人物身份未决，不连接作者KU。|
| st-chp17-pi-note6-cites-tassini-1887 | formal rel-{start+6:04d} `cites`：Haskell→第四版1887图书。|
| st-chp17-p380-note4-meschini-gallery-description | pending `has_subject`：引用书映射已完成；gallery/collection候选cand-1513仍无支持类型。|
| st-chp17-p380-note6-edwards-letter-source | formal reuse rel-1593 `part_of`：Manfrin–Edwards书信→Epistolario Moschini；不重复造边。|
| st-chp17-p381-note1-moschini-1806 | formal reuse rel-{start+1:04d} `cites`：同一1806出版物及卷页。|
| st-chp17-p381-note1-moschini-1810 | pending `cites`：只给年份与same-author，没有题名、卷页或可识别出版物KU。|

不新增`located_at`关系行；其物理/书内馆藏定位候选保留pending与解除条件。`rel-1592`记录Epistolario系列→Correr Library的既有边；本批对书信本身复用rel-1593的series membership。

#### S4/S5写回范围

登记5张archive KU（Moschini四卷本、Correr手稿、两条Inquisitori登记、Tassini第四版），修正2条历史S3-new决定与3条触发身份决定为same；修复cand-9448“new但已指向既有KU”的状态。新卡27条Haskell来源S5字段；既有pamphlet卡7条字段补入来源标记并按印本页图更新。source corpus及原始OCR未改写。

**批后审计：** 待本脚本apply后运行严格表审计、关系一致性审计、字段预览和定向卡片预览；此处数字将在核验完成后补录。
"""
    stages_note = f"""

### {DATE}：第17章p.379–381引注页图触发的S2修订与S3–S6端点批次

按当前候选、关系statement及CHP-17印本扫描逐项复核。S0源文件只读。p.379–381图像将多处OCR差异校正记入statement qualifiers；p.379注1/注2/注3/注4/注5/注6新增独立Haskell-cites statements共6条。p.380注4的quoted source端点改为Moschini出版物→Manfrin gallery候选；p.380注6改为书信→Epistolario系列；p.381注1改为Haskell书→1806出版物，1810未识别文献保持candidate端点并转为Haskell书→候选文献。反转p.379注2/注4/注5的档案位置statement方向。新增statement不增加mention，不计入S2统一独立复核分子；本次不宣称第17章或S2独立接收。

详见[第17章来源端点过程记录](knowledge.md#{ANCHOR})。批后statement/mention计数和严格审计将在S4/S6写回后补入。
"""
    process_new = process.rstrip() + process_note
    stages_new = stages.rstrip() + stages_note
    writes[paths["process"]] = (b"\xef\xbb\xbf" if paths["process"].read_bytes().startswith(b"\xef\xbb\xbf") else b"") + process_new.encode("utf-8")
    writes[paths["stages"]] = (b"\xef\xbb\xbf" if paths["stages"].read_bytes().startswith(b"\xef\xbb\xbf") else b"") + stages_new.encode("utf-8")
    print("S3 changes:", ", ".join(f"{cid}:{primary[cid]['decision']}->{primary[cid]['ku_id']}" for cid in SAME))
    print(f"S4: {len(SPECS)} new archive KUs; S5 preview={len(field_rows)} rows (27 new, 7 updated; all source_backed)")
    print(f"S2: +{len(new_statements)} atomic citation statements; mentions unchanged; S6 decisions=16 (9 formal/reuse, 7 pending)")
    print(f"S6 formal rows planned={len(relation_specs)}; rel-{start:04d}–rel-{start+len(relation_specs)-1:04d}; reuse rel-1593")
    print("Pending: four located_at statements (needs_split), Tassini authorship, untyped gallery subject, unidentified 1810 citation.")
    print("Writes:", len(writes), "files plus", len(card_texts), "cards")
    if args.dry_run:
        return 0
    recovery = ROOT / "06-runtime/recovery/S4-S6-ch17-p379-p381-manfrin-20261026"
    recovery.mkdir(parents=True, exist_ok=False)
    manifest_hashes = {}
    for path in writes:
        relative = path.relative_to(ROOT)
        if path.exists():
            original = path.read_bytes()
            backup = recovery / "original" / relative
            backup.parent.mkdir(parents=True, exist_ok=True)
            backup.write_bytes(original)
            manifest_hashes[relative.as_posix()] = hashlib.sha256(original).hexdigest()
        else:
            manifest_hashes[relative.as_posix()] = None
    (recovery / "backup-manifest.json").write_text(json.dumps(manifest_hashes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for path, content in writes.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    print(f"applied; recovery={recovery.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
