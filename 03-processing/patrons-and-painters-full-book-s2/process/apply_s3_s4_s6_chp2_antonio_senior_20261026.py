#!/usr/bin/env python3
"""Register the elder Antonio Barberini identity and its supported endpoints.

Default mode is a read-only preflight. The apply mode requires the exact live
S3 rows and relation-table boundary recorded for this batch.
"""
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
HELPER = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "apply_s3_s4_s6_chp2_emblems_20261026.py"
PROCESS_REF = "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp2-emblems-endpoints-20261026"
TASK = "patrons-and-painters-full-book-s2"
TODAY = "2026-10-26"
TRECCANI_URL = "https://www.treccani.it/enciclopedia/antonio-barberini_res-2ec798e4-87e7-11dc-8e9d-0016357eee51_(Dizionario-Biografico)/"
TRECCANI_CITATION = f"Alberto Merola, ‘BARBERINI, Antonio,’ Dizionario Biografico degli Italiani, vol. 6 (1964), Treccani. {TRECCANI_URL} Accessed {TODAY}."
HASKELL_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)."
SENIOR_ID = "units/persons/antonio-barberini-senior"
MONASTERY_ID = "units/places/capuchin-monastery-on-the-pincio"
GROUP_ID = "new-person:antonio-barberini-elder-cand-0186-20261026"


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bool, str]:
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    rows = list(csv.DictReader(io.StringIO(text, newline="")))
    header = list(rows[0].keys()) if rows else next(csv.reader(io.StringIO(text)))
    return header, rows, bom, newline


def patch_csv(path: Path, key_field: str, updates: dict[str, dict[str, str]], appends: list[dict[str, str]] | None = None) -> bytes:
    header, rows, bom, newline = read_csv(path)
    by_key = {row[key_field]: row for row in rows}
    if set(updates) - set(by_key):
        raise ValueError(f"{path.name}: missing update keys {sorted(set(updates) - set(by_key))}")
    for key, values in updates.items():
        by_key[key].update(values)
    appends = appends or []
    append_keys = [row[key_field] for row in appends]
    if len(append_keys) != len(set(append_keys)) or set(append_keys) & set(by_key):
        raise ValueError(f"{path.name}: duplicate appended key")
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=header, extrasaction="ignore", lineterminator=newline)
    writer.writeheader()
    for row in rows:
        writer.writerow(by_key[row[key_field]])
    writer.writerows(appends)
    return (b"\xef\xbb\xbf" if bom else b"") + output.getvalue().encode("utf-8")


def source(citation: str, location: str, summary: str, source_file: str, span: str, quote: str = "") -> dict:
    result = {
        "citation": citation,
        "location": location,
        "sentence_summary": summary,
        "evidence_ref": {"doc_id": "patrons-and-painters" if source_file.startswith("02-sources/") else TRECCANI_URL,
                         "source_file": source_file, "source_span": span},
    }
    if quote:
        result["original_quotes"] = [{"source_span": span, "text": quote}]
    return result


def card_bytes(title: str, name_en: str, type_name: str, sources: list[dict], sections: list[tuple[str, list[tuple[str, str, str]]]], description_zh: str, description_en: str, process_ref: str) -> bytes:
    front = {
        "title": f"{title}（{name_en}）",
        "name_en": name_en,
        "type": type_name,
        "evidence_status": "source_backed",
        "sources": sources,
        "created": TODAY,
        "updated": TODAY,
        "process_ref": process_ref,
    }
    text = ["---", yaml.safe_dump(front, sort_keys=False, allow_unicode=True, width=110).rstrip(), "---", "", "## 内容", "", "### 描述", f"**中文：** {description_zh}", f"**English:** {description_en}", ""]
    for heading, rows in sections:
        text.extend([f"### {heading}", "", "| 字段 | 值 | 证据 |", "|---|---|---|"])
        text.extend(f"| {a} | {b} | {c} |" for a, b, c in rows)
        text.append("")
    text.extend(["### 本章相关内容", "本卡保留哈斯克尔明确描述的身份与活动范围；关系端点以 S6 受控记录生成。", "", "## 关系与证据", "", "### 身份与外部链接", f"[Treccani，《BARBERINI, Antonio》，Dizionario Biografico degli Italiani 6 (1964)]({TRECCANI_URL}) — 用于区分同名叔侄并记录来源所述生平。", "", "### 关系记录", ""])
    return ("\n".join(text) + "\n").encode("utf-8")


def build() -> dict[Path, bytes]:
    if not HELPER.exists():
        raise ValueError("the already-applied Chapter 2 endpoint plan is missing")
    import runpy
    base = runpy.run_path(str(HELPER))
    planned = base["RELATION_CANDIDATES"]
    if len(planned) != 9:
        raise ValueError("expected the reviewed 9-row Chapter 2 emblem relation plan")

    ch2 = "02-sources/02-Markdown/02_CHP-2_sec_ii.md"
    ch2iv = "02-sources/02-Markdown/02_CHP-2_sec_iv.md"
    senior_sources = [
        source(HASKELL_CITATION, "第2章，印刷页31；PDF物理页16；L3–4", "Haskell称Urban VIII的兄弟Antonio在枢机任命序列中随后取得相同身份。", ch2, "lines 3–4; print p. 31; PDF physical p. 16", "a year later his brother Antonio, a Capuchin monk, received the same dignity"),
        source(HASKELL_CITATION, "第2章，印刷页42；PDF物理页27；L132–134", "Haskell记述Antonio于1626年决定为嘉布遣会兴建新教堂及修道院，并称他是Urban VIII的弟弟。", ch2, "lines 132–134; print p. 42; PDF physical p. 27", "In 1626 he decided to have built for his Order a new church"),
        source(HASKELL_CITATION, "第2章，印刷页43；PDF物理页28；L143–144", "Haskell记载Cardinal S. Onofrio订置并送达木制烛台与十字架，并与Urban VIII共同委托祭坛画。", ch2, "lines 143–144; print p. 43; PDF physical p. 28", "Cardinal S. Onofrio ordered a dozen candlesticks and two crucifixes"),
        source(HASKELL_CITATION, "第2章，印刷页52；PDF物理页37；L99", "Haskell称Urban VIII令Bracciolini担任其嘉布遣会兄弟Antonio的秘书，并记Antonio于1627年成为Sinigaglia主教。", ch2iv, "line 99; print p. 52; PDF physical p. 37", "his austere Capuchin brother Antonio who in 1627 became Bishop of Sinigaglia"),
        source(TRECCANI_CITATION, "条目标题及传记开篇，lines 21–30", "Merola记其受洗名Marcello、其兄Maffeo于1623年成为教皇、1624年获枢机身份、1625年获任Senigallia主教、1627年主持教区会议，并记1569–1646年生卒。", TRECCANI_URL, "entry heading and lines 21–30", "Nel 1623, quando il fratello Maffeo divenne pontefice"),
    ]
    senior = card_bytes(
        "安东尼奥·巴贝里尼（年长者）", "Antonio Barberini senior", "person", senior_sources,
        [("姓名与身份", [
            ("来源称名", "Antonio Barberini；Treccani 记其受洗名为 Marcello，父亲去世后改用 Antonio。", "S5；DBI lines 24–25"),
            ("亲属关系", "Urban VIII（Maffeo Barberini）的弟弟；与Urban VIII的侄子、小安东尼奥（1607–1671）分属两人。", "S1；第2章印刷页42 L132；S5；DBI lines 24–25"),
            ("消歧范围", "本卡只指年长的Antonio Barberini；不把年轻侄子的家户、作品或任职并入本卡。", "S1–S5；跨章身份比较"),
        ]), ("基本信息", [
            ("生卒", "1569–1646", "S5；DBI lines 24–30"),
            ("宗教身份", "嘉布遣会修士；枢机称号为Cardinal di S. Onofrio。", "S1；第2章印刷页31、42–43"),
            ("枢机身份", "Treccani记1624年10月7日获枢机身份；Haskell将其置于Francesco之后一年。", "S1；第2章印刷页31 L3–4；S5；DBI lines 24–25"),
            ("Senigallia主教", "Haskell称1627年成为主教；DBI称1625年获任并记1627年主持教区会议。保留来源日期差异，不合并为单一任命年。", "S4；第2章印刷页52 L99；S5；DBI lines 25–26"),
        ]), ("本章相关活动", [
            ("建堂决定", "Haskell称其于1626年决定为嘉布遣会兴建新教堂和修道院；本章未证明两者完工。", "S2；第2章印刷页42 L132–134"),
            ("圣器订置与送达", "Haskell称Cardinal S. Onofrio订置十二支木制烛台及两件木制十字架，并送往S. Maria della Concezione。来源未指明制造者或安装状态。", "S3；第2章印刷页43 L143"),
            ("祭坛画委托", "Haskell称Urban VIII与其兄弟Antonio共同委托祭坛画；作品总数及完整成员未知。", "S3；第2章印刷页43 L144"),
            ("秘书任命", "Haskell称Urban VIII令Bracciolini担任其嘉布遣会兄弟Antonio的秘书；本章未给该任命日期。", "S4；第2章印刷页52 L99"),
        ])],
        "此卡记录Urban VIII的兄弟、年长枢机Antonio Barberini（受洗名Marcello），与侄辈Antonio Barberini the Younger分开。Haskell的教区年份与Merola的DBI条目所记任命年存在差异，分别保留来源归属。",
        "This card records Antonio Barberini senior, baptized Marcello, the brother of Urban VIII and uncle of Antonio Barberini the Younger. Haskell's date for his bishopric differs from Merola's DBI account; both source-attributed dates are retained.",
        PROCESS_REF,
    )
    monastery_sources = [source(HASKELL_CITATION, "第2章，印刷页42；PDF物理页27；L132–134", "Haskell称Antonio于1626年决定为嘉布遣会兴建一座新教堂和修道院，并把修道院位置与Ludovisi枢机地产、Pincio关联。", ch2, "lines 132–134; print p. 42; PDF physical p. 27", "and monastery adjoining the estates of Cardinal Ludovisi on the Pincio")]
    monastery = card_bytes(
        "皮恩乔山嘉布遣会修道院计划", "Capuchin Monastery Project on the Pincio", "place", monastery_sources,
        [("基本信息", [
            ("对象类型", "嘉布遣会修道院地点候选；与同一建设决定中的罗马嘉布遣会教堂分别登记。", "S1；第2章印刷页42 L132–134"),
            ("来源所述状态", "Antonio Barberini于1626年决定兴建；Haskell没有在本段证明修道院完工。", "S1；第2章印刷页42 L132–134"),
            ("位置描述", "与Ludovisi枢机地产相邻，位于Pincio语境；不据此推定与教堂建筑本身相邻或精确地块。", "S1；第2章印刷页42 L132–134"),
        ])],
        "本卡只记录哈斯克尔所述的修建计划，不将计划写成已完成建筑。",
        "This unit records only the building project reported by Haskell; it does not treat the plan as proof that the monastery was completed.",
        PROCESS_REF,
    )

    senior_path = UNITS / "persons" / "antonio-barberini-senior.md"
    monastery_path = UNITS / "places" / "capuchin-monastery-on-the-pincio.md"
    if senior_path.exists() or monastery_path.exists():
        raise ValueError("one of the target cards already exists")

    alignment_path = TABLES / "alignment.csv"
    _, alignments, _, _ = read_csv(alignment_path)
    old = next(r for r in alignments if r["alignment_id"] == "aln-0521")
    if old["candidate_id"] != "cand-0186" or old["decision"] != "same" or old["ku_id"] != "units/persons/antonio-barberini":
        raise ValueError("cand-0186 no longer has the expected false same decision")
    mon = next(r for r in alignments if r["alignment_id"] == "aln-4705")
    if mon["candidate_id"] != "cand-4522" or mon["decision"] != "new" or mon["ku_id"]:
        raise ValueError("cand-4522 is no longer an unmapped new candidate")
    prior = old["resolution_note"]
    group_note = (f"prior_decision=same; prior_ku=units/persons/antonio-barberini; prior_resolution_note={prior}; "
                  f"S3 correction 2026-10-26: cand-0186 is Antonio Barberini senior, baptized Marcello, brother of Urban VIII (Maffeo), not his nephew Antonio Barberini the Younger (cand-0187; 1607–1671). Haskell ch.2 pp.31,42,43,52 supplies the cardinal, kinship, Capuchin, commission, furnishing and secretary anchors. Alberto Merola, DBI 6 (1964), entry BARBERINI, Antonio, lines 24–30 distinguishes the elder (1569–1646), gives baptismal name Marcello, and records his brother Maffeo as Urban VIII. New identity group={GROUP_ID}; S4={SENIOR_ID}; see {PROCESS_REF}.")
    mon_note = mon["resolution_note"] + f" S4 registration 2026-10-26: existing S3 new group for the separately described Capuchin monastery project mapped to {MONASTERY_ID}; completion and precise parcel remain unverified. See {PROCESS_REF}."
    changes: dict[Path, bytes] = {
        senior_path: senior,
        monastery_path: monastery,
        alignment_path: patch_csv(alignment_path, "alignment_id", {
            "aln-0521": {"ku_id": SENIOR_ID, "external_source": "Treccani DBI: BARBERINI, Antonio (1569–1646)", "external_id": TRECCANI_URL, "decision": "new", "accessed_date": TODAY, "process_ref": PROCESS_REF, "resolution_note": group_note},
            "aln-4705": {"ku_id": MONASTERY_ID, "process_ref": PROCESS_REF, "resolution_note": mon_note},
        }),
        TABLES / "entity-candidates.csv": patch_csv(TABLES / "entity-candidates.csv", "candidate_id", {
            "cand-0186": {"detail": "Urban VIII (Maffeo Barberini) 的兄弟、枢机 Cardinal di S. Onofrio；与侄辈 Cardinal Antonio Barberini the Younger（cand-0187）区分。Treccani DBI条目记受洗名Marcello，生卒1569–1646；S3新人物组new-person:antonio-barberini-elder-cand-0186-20261026。"},
            "cand-4522": {"detail": "哈斯克尔第2章印刷页42称1626年为嘉布遣会决定兴建新修道院，位置关联Pincio与Ludovisi地产；计划不证明完工。S4映射 units/places/capuchin-monastery-on-the-pincio。"},
        }),
        TABLES / "ku-manifest.csv": patch_csv(TABLES / "ku-manifest.csv", "ku_id", {}, [
            {"ku_id": SENIOR_ID, "type": "person", "canonical_name": "安东尼奥·巴贝里尼（年长者）", "name_en": "Antonio Barberini senior", "source_task": TASK, "card_path": "04-knowledge/units/persons/antonio-barberini-senior.md"},
            {"ku_id": MONASTERY_ID, "type": "place", "canonical_name": "皮恩乔山嘉布遣会修道院计划", "name_en": "Capuchin Monastery Project on the Pincio", "source_task": TASK, "card_path": "04-knowledge/units/places/capuchin-monastery-on-the-pincio.md"},
        ]),
    }
    accepted = ROOT / "04-knowledge" / "accepted.yml"
    raw = accepted.read_bytes(); text = raw.decode("utf-8-sig"); bom = raw.startswith(b"\xef\xbb\xbf")
    nl = "\r\n" if "\r\n" in text else "\n"; lines = text.splitlines(keepends=True)
    new_entries = ["- 04-knowledge/units/persons/antonio-barberini-senior.md", "- 04-knowledge/units/places/capuchin-monastery-on-the-pincio.md"]
    if any(x in [line.rstrip("\r\n") for line in lines] for x in new_entries):
        raise ValueError("one or more new cards already occur in accepted.yml")
    claims = next((i for i, line in enumerate(lines) if line.rstrip("\r\n") == "claims:"), None)
    if claims is None:
        raise ValueError("accepted.yml has no claims section")
    lines[claims:claims] = [x + nl for x in new_entries]
    changes[accepted] = (b"\xef\xbb\xbf" if bom else b"") + "".join(lines).encode("utf-8")

    relations_path = TABLES / "relations.csv"
    _, relations, _, _ = read_csv(relations_path)
    last = max(int(r["relation_id"].removeprefix("rel-")) for r in relations)
    if last != 2271:
        raise ValueError(f"expected rel-2271 as current maximum, found rel-{last}")
    rows = []
    for spec in planned:
        rows.append({"subject_ku_id": spec["subject"], "object_ku_id": spec["object"], "predicate": spec["predicate"], "time": spec.get("time", ""), "role": spec["role"], "scope": spec["scope"], "origin": "book", "status": "formal", "source_id": "haskell-1980-rev-ed", "source_span": spec["span"], "source_file": spec["file"], "note": f"S2 statement: {spec['statement']}. Haskell source-scoped relation; see {PROCESS_REF}."})
    rows.extend([
        {"subject_ku_id": SENIOR_ID, "object_ku_id": "units/persons/urbano-viii", "predicate": "appointed_by", "time": "1624-10-07", "role": "枢机授任关系；任命日期据DBI", "scope": "Haskell的相邻叙述把Antonio取得枢机身份放在Urban VIII兄弟关系中但未直接陈述授任者；DBI确认Antonio于1624-10-07获枢机身份。此边保留该来源语境，任命执行人仍按原文隐含关系处理。", "origin": "book", "status": "formal", "source_id": "haskell-1980-rev-ed", "source_span": "Chapter 2, print p. 31, lines 3–4; Treccani DBI 6 (1964), entry BARBERINI, Antonio, lines 24–25", "source_file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md", "note": f"S2 statement: st-chp2-sec-ii-l3-8-antonio-brother-cardinal. Identity/date corroboration: {TRECCANI_URL}. The passage leaves the appointing agent implicit; see {PROCESS_REF}."},
        {"subject_ku_id": "units/places/capuchin-church-rome", "object_ku_id": SENIOR_ID, "predicate": "commissioned_by", "time": "1626", "role": "新教堂兴建决定者", "scope": "Haskell称Antonio决定为其修会兴建新教堂；本段未证明工程完成。", "origin": "book", "status": "formal", "source_id": "haskell-1980-rev-ed", "source_span": "Chapter 2, print p. 42, lines 132–133", "source_file": ch2, "note": f"S2 statement: st-chp2-secii-l127-139-antonio-decides-church. Source reports a decision to build, not completion; see {PROCESS_REF}."},
        {"subject_ku_id": MONASTERY_ID, "object_ku_id": SENIOR_ID, "predicate": "commissioned_by", "time": "1626", "role": "修道院建设计划的决定者", "scope": "Haskell称Antonio决定为嘉布遣会兴建修道院；位置描述关联Ludovisi地产与Pincio，不证明完工或精确地块。", "origin": "book", "status": "formal", "source_id": "haskell-1980-rev-ed", "source_span": "Chapter 2, print p. 42, lines 132–134", "source_file": ch2, "note": f"S2 statement: st-chp2-secii-l127-139-antonio-decides-monastery. The project remains reported/planned; see {PROCESS_REF}."},
        {"subject_ku_id": SENIOR_ID, "object_ku_id": "units/persons/urbano-viii", "predicate": "sibling_of", "time": "", "role": "Urban VIII的弟弟", "scope": "Haskell称Antonio为Urban VIII的弟弟；Treccani DBI独立记录其兄弟Maffeo于1623年成为教皇。", "origin": "book", "status": "formal", "source_id": "haskell-1980-rev-ed", "source_span": "Chapter 2, print p. 42, line 132; Treccani DBI 6 (1964), entry BARBERINI, Antonio, line 24", "source_file": ch2, "note": f"S2 statement: st-chp2-secii-l127-139-antonio-urban-sibling. Identity support: {TRECCANI_URL}. See {PROCESS_REF}."},
        {"subject_ku_id": SENIOR_ID, "object_ku_id": "units/institutions/capuchins", "predicate": "member_of", "time": "", "role": "嘉布遣会修士", "scope": "Haskell第2章印刷页42及52两处称其为Capuchin；合并为同一身份关系，保留两条S2来源锚点。", "origin": "book", "status": "formal", "source_id": "haskell-1980-rev-ed", "source_span": "Chapter 2, print p. 42, line 132; print p. 52, line 99; S2 statements st-chp2-secii-l127-139-antonio-capuchin-membership and st-chp2-seciv-l96-104-antonio-capuchin", "source_file": ch2, "note": f"Two source passages support one membership edge; see {PROCESS_REF}."},
        {"subject_ku_id": "units/persons/francesco-bracciolini", "object_ku_id": SENIOR_ID, "predicate": "employed_by", "time": "", "role": "秘书", "scope": "Haskell称Urban VIII令Bracciolini担任其嘉布遣会兄弟Antonio的秘书；记录工作对象和角色，不推定任命日期。", "origin": "book", "status": "formal", "source_id": "haskell-1980-rev-ed", "source_span": "Chapter 2, print p. 52, line 99", "source_file": ch2iv, "note": f"S2 statement: st-chp2-seciv-l96-104-bracciolini-secretary-to-antonio. Appointer is Urban VIII; no date is supplied; see {PROCESS_REF}."},
    ])
    existing_keys = {(r["subject_ku_id"], r["object_ku_id"], r["predicate"], r["time"]) for r in relations}
    for row in rows:
        key = (row["subject_ku_id"], row["object_ku_id"], row["predicate"], row["time"])
        if key in existing_keys:
            raise ValueError(f"duplicate relation natural key {key}")
        existing_keys.add(key)
    for index, row in enumerate(rows, start=last + 1):
        row["relation_id"] = f"rel-{index}"
    relation_updates = {
        "rel-1390": {"object_ku_id": SENIOR_ID, "role": "年长Cardinal S. Onofrio为订置并送达物件的提供者", "scope": "Haskell称年长Antonio Barberini订置并将该组物件送往the church；不推定制造者、创作者或安装状态。"},
        "rel-1391": {"object_ku_id": SENIOR_ID, "role": "年长Cardinal S. Onofrio为订置并送达物件的提供者", "scope": "Haskell称年长Antonio Barberini订置并将该组物件送往the church；不推定制造者、创作者或安装状态。"},
        "rel-1674": {"object_ku_id": SENIOR_ID, "role": "Urban VIII之兄为共同委托人", "scope": "Haskell称Urban VIII与其兄弟委托祭坛画；兄弟身份对应年长Antonio Barberini而非其侄子。作品总数与完整成员仍未知。"},
    }
    if len(rows) != 15:
        raise ValueError(f"expected 15 new formal rows, got {len(rows)}")
    changes[relations_path] = patch_csv(relations_path, "relation_id", relation_updates, rows)

    for rel_id in relation_updates:
        if not any(r["relation_id"] == rel_id for r in relations):
            raise ValueError(f"missing existing relation {rel_id}")
    return changes


def apply(changes: dict[Path, bytes], do_apply: bool) -> None:
    changed = {path: raw for path, raw in changes.items() if not path.exists() or path.read_bytes() != raw}
    print(json.dumps({"mode": "apply" if do_apply else "preflight", "files": len(changed), "paths": [p.relative_to(ROOT).as_posix() for p in changed], "formal_relation_rows": 15, "corrected_existing_relation_endpoints": 3}, ensure_ascii=False, indent=2))
    if not do_apply or not changed:
        return
    originals = {path: path.read_bytes() if path.exists() else None for path in changed}
    applied: list[Path] = []
    try:
        for path, raw in changed.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
            applied.append(path)
    except Exception:
        for path in reversed(applied):
            old = originals[path]
            if old is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(old)
        raise
    print(f"Applied {len(applied)} files; the pre-apply state is retained in 06-runtime/recovery/s3-s4-s6-antonio-senior-20261026-before.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    apply(build(), args.apply)


if __name__ == "__main__":
    main()
