#!/usr/bin/env python3
"""
build_tables.py — 第 5 步：按新规范生成 04-knowledge/tables/，并导出 release/v0.1/ 冻结快照。

只读现有数据，不调用外部接口。迁移映射见 01-domain/stage-artifact-schema.md 0.4 节。
- ku_id 统一不带 .md；candidate/relation/enrichment/alignment 用单调发号（永不重编）。
- origin ∈ {book, external, inferred}；align 不再是 origin（身份映射进 alignment.csv 的 decision）。
- evidence_status 用 5 值（默认 unverified）。
- enrichment-evidence 中只有 QID 的「身份证据」归入 alignment 的 external_id，不留在 enrichment。
- S0 补 sources.csv + segments.jsonl（分节文件切段 + 内容哈希）。
"""
import csv
import hashlib
import io
import json
import re
import yaml
from pathlib import Path
from collections import Counter, defaultdict

BASE = Path(__file__).resolve().parents[1]
TABLES = BASE / "04-knowledge" / "tables"
RELEASE = BASE / "release" / "v0.1"
IDX = BASE / "02-sources" / "03-Index" / "03-2-Index-CSV"
MARKDOWN = BASE / "02-sources" / "02-Markdown"

TYPE_SINGULAR = {
    "persons": "person", "families": "family", "institutions": "institution",
    "places": "place", "works": "work", "archives": "archive",
    "terms": "term", "procedures": "procedure", "events": "event",
}

_next = defaultdict(int)


def next_id(prefix):
    _next[prefix] += 1
    return f"{prefix}-{_next[prefix]:04d}"


def norm_ku(path):
    p = str(path).replace("\\", "/").rstrip("/")
    p = re.sub(r"^04-knowledge/", "", p)
    p = re.sub(r"^units/", "", p)
    p = re.sub(r"\.md$", "", p)
    return f"units/{p}"


def read_fm(path):
    try:
        txt = open(path, encoding="utf-8").read(3000)
    except Exception:
        return ""
    if txt.startswith("---"):
        parts = txt.split("---", 2)
        return parts[1] if len(parts) >= 2 else ""
    return ""


def fm_field(fm, field):
    m = re.search(rf"^{re.escape(field)}:\s*(.+)$", fm, re.MULTILINE)
    return m.group(1).strip().strip("'\"") if m else ""


def split_title(title, name_en):
    if not name_en:
        m = re.match(r"^([^（(]*)[（(](.*)[）)]$", title.strip())
        if m:
            return m.group(1).strip(), m.group(2).strip()
        return title.strip(), ""
    for lp, rp in (("（", "）"), ("(", ")")):
        cand = title.replace(f"{lp}{name_en}{rp}", "").strip()
        if cand != title:
            return cand, name_en
    return title.strip(), name_en


def read_jsonl(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except Exception:
                    pass
    return out


def derive_origin(evidence_ref):
    er = evidence_ref or {}
    sf = er.get("source_file", "") or ""
    doc = er.get("doc_id", "") or ""
    if sf.startswith("02-sources") or doc == "patrons-and-painters":
        return "book"
    if isinstance(sf, str) and sf.startswith("http"):
        return "external"
    return "inferred"


def write_csv(path, rows, cols):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def read_index_entries():
    """读原书索引 CSV，返回 [(main_entry, file, row)]，去重（同主条并页码）。"""
    entries = []
    for f in sorted(IDX.glob("*.csv")):
        data = f.read_bytes()
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = data.decode("gb18030")
        for i, r in enumerate(csv.DictReader(io.StringIO(text))):
            me = (r.get("Main Entry") or "").strip()
            if not me:
                continue
            sub = (r.get("Sub-entry") or "").strip()
            detail = (r.get("Detail") or "").strip()
            if "see under" in (sub + " " + detail).lower():
                continue
            entries.append((me, (r.get("Page Numbers") or "").strip(), f.name, i))
    return entries


def main():
    TABLES.mkdir(parents=True, exist_ok=True)
    RELEASE.mkdir(parents=True, exist_ok=True)

    # ---- S0 sources.csv ----
    sources_rows = [{
        "source_id": "haskell-1980-rev-ed",
        "kind": "book",
        "label": "Francis Haskell, Patrons and Painters, revised and enlarged edition (Yale UP, 1980)",
        "version": "revised and enlarged edition",
        "accessed_date": "",
    }]
    write_csv(TABLES / "sources.csv", sources_rows, ["source_id", "kind", "label", "version", "accessed_date"])

    # ---- S0 segments.jsonl（分节文件切段）----
    seg_rows = []
    seen = set()
    for f in sorted(MARKDOWN.glob("*.md")):
        name = f.name
        # 只用分节文件：跳过整章文件（如 01_CHP-1.md）和 _intro（保留 intro，因属于分节）
        if re.match(r"^\d+_CHP-\d+\.md$", name):
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        paras = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
        for pi, para in enumerate(paras, 1):
            lines = para.strip().splitlines()
            h = hashlib.sha256(para.encode("utf-8")).hexdigest()[:16]
            seg_rows.append({
                "segment_id": f"{name}:p{pi}",
                "chapter": name.split("_")[0],
                "section": name,
                "line_start": pi,
                "line_end": pi + len(lines) - 1,
                "sha256": h,
                "release_excluded": True,
            })
    with open(TABLES / "segments.jsonl", "w", encoding="utf-8") as f:
        for r in seg_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # ---- S1 entity-candidates.csv（单调 cand-N）----
    entries = read_index_entries()
    cand_rows, by_name = [], defaultdict(list)
    for me, pages, file, row in entries:
        cid = next_id("cand")
        cand_rows.append({
            "candidate_id": cid,
            "index_entry_id": f"{file}#{row}",
            "canonical_name": me,
            "index_page_range": pages,
            "suggested_type": "",
            "status": "open",
        })
        by_name[me.lower().strip("'\"")].append(cid)
    write_csv(TABLES / "entity-candidates.csv", cand_rows,
              ["candidate_id", "index_entry_id", "canonical_name", "index_page_range", "suggested_type", "status"])

    # ---- S4 ku-manifest.csv（ku_id 不带 .md）----
    accepted = yaml.safe_load(open(BASE / "04-knowledge/accepted.yml", encoding="utf-8"))
    unit_paths = accepted.get("units", [])
    ku_rows = []
    ku_set = set()
    for up in unit_paths:
        parts = up.rstrip(".md").split("/")
        dir_ = parts[-2]
        typ = TYPE_SINGULAR.get(dir_, dir_)
        ku_id = norm_ku(up)
        ku_set.add(ku_id)
        fm = read_fm(BASE / up)
        zh, en = split_title(fm_field(fm, "title"), fm_field(fm, "name_en"))
        pr = fm_field(fm, "process_ref")
        src_task = next((t for t in ("front-matter", "chp-1", "chp-6") if t in pr), "")
        ku_rows.append({
            "ku_id": ku_id, "type": typ, "canonical_name": zh, "name_en": en,
            "source_task": src_task, "card_path": up,
        })
    write_csv(TABLES / "ku-manifest.csv", ku_rows,
              ["ku_id", "type", "canonical_name", "name_en", "source_task", "card_path"])

    # ---- S6 relations.csv（现在为源，不再从 relation-index.yml 生成）----
    # 读取现有 relations.csv，仅用于统计与域值域检查；不再重写它。
    rel_rows = list(csv.DictReader(open(TABLES / "relations.csv", encoding="utf-8")))
    origin_count, status_count, pred_count = Counter(), Counter(), Counter()
    for r in rel_rows:
        origin_count[r.get("origin", "")] += 1
        status_count[r.get("status", "")] += 1
        pred_count[r.get("predicate", "")] += 1

    # ---- S3 alignment.csv（decision；合并 enrichment-evidence 的 QID）----
    # 名字 -> 候选（用 index 的候选，做粗匹配回填 candidate_id）
    norm_cand = {}
    for r in cand_rows:
        n = re.sub(r"[^a-z0-9]+", " ", r["canonical_name"].lower()).strip()
        if n:
            norm_cand.setdefault(n, r["candidate_id"])

    def match_candidate(ku_row):
        for fld in ("name_en", "canonical_name"):
            n = re.sub(r"[^a-z0-9]+", " ", ku_row[fld].lower()).strip()
            if n and n in norm_cand:
                return norm_cand[n]
        return None

    align_rows = []
    aln = read_jsonl(BASE / "03-processing/patrons-and-painters-chp-1/process/alignment-evidence.jsonl")
    for a in aln:
        key = a.get("key", "")
        ku_id = norm_ku(key)
        st = a.get("status", "unpaired")
        sem = a.get("semantic_decision", "")
        if st == "paired":
            decision = "same"
        elif re.search(r"排除|误配|不适用|范围不符|候选排除", sem):
            decision = "excluded"
        else:
            decision = "undecided"
        align_rows.append({
            "alignment_id": next_id("aln"),
            "candidate_id": "",
            "ku_id": ku_id,
            "external_source": "Wikidata" if a.get("confirmed_qid") else "",
            "external_id": a.get("confirmed_qid") or "",
            "decision": decision,
            "accessed_date": a.get("access_date", ""),
            "process_ref": a.get("review", ""),
        })
    # 合并 enrichment-evidence 的 QID（身份证据）
    enr = read_jsonl(BASE / "03-processing/patrons-and-painters-chp-1/process/enrichment-evidence.jsonl")
    qid_by_unit = {}
    for e in enr:
        u = norm_ku(e.get("unit", ""))
        q = e.get("qid", "")
        if q and u:
            qid_by_unit.setdefault(u, q)
    for r in align_rows:
        if not r["external_id"] and r["ku_id"] in qid_by_unit:
            r["external_id"] = qid_by_unit[r["ku_id"]]
            r["external_source"] = "Wikidata"
    # 回填 candidate_id（粗匹配；匹配不到留空，待建候选）
    ku_lookup = {r["ku_id"]: r for r in ku_rows}
    for r in align_rows:
        kr = ku_lookup.get(r["ku_id"])
        if kr:
            r["candidate_id"] = match_candidate(kr) or ""
    write_csv(TABLES / "alignment.csv", align_rows,
              ["alignment_id", "candidate_id", "ku_id", "external_source", "external_id", "decision",
               "accessed_date", "process_ref"])

    # ---- S5 enrichment.jsonl（origin=external，evidence_status 默认 unverified）----
    # 字段级内容事实在卡内正文，本轮只记录来源级（unit ← 外部来源），field/value 留空待深解析。
    with open(TABLES / "enrichment.jsonl", "w", encoding="utf-8") as f:
        for e in enr:
            sem = str(e.get("semantic_review", ""))
            if sem == "reviewed":
                evs = "externally_verified"
            elif "gaps" in sem.lower():
                evs = "source_backed"
            else:
                evs = "unverified"
            rec = {
                "enrichment_id": next_id("enr"),
                "ku_id": norm_ku(e.get("unit", "")),
                "field": "",
                "value": "",
                "origin": "external",
                "source_id": "wikidata" if "wikidata" in (e.get("url", "") or "").lower() else "",
                "url": e.get("url", ""),
                "evidence_status": evs,
                "dispute": False,
                "accessed_date": e.get("access_date", ""),
                "process_ref": e.get("review", ""),
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # ---- id-redirects.csv（空表，供后续改名登记）----
    write_csv(TABLES / "id-redirects.csv", [], ["old_id", "new_id", "reason", "date"])

    # ---- S7 release 快照（从 tables 复制，排除含原书全文的 segments）----
    for f in TABLES.glob("*"):
        if f.name in ("id-redirects.csv", "segments.jsonl"):
            continue  # 重定向表只内部用；segments 含原书全文，不发布
        (RELEASE / f.name).write_bytes(f.read_bytes())

    # ---- validation-report.md ----
    lines = [
        "# v0.1 发布验证报告（第 5 步重新导出）",
        "",
        "## 统计",
        "",
        "| 指标 | 值 |",
        "|---|---|",
        f"| 有效知识元（KU） | {len(ku_rows)} |",
        f"| 正式关系边 | {len(rel_rows)} |",
        f"| 全书实体候选 | {len(cand_rows)} |",
        f"| 对齐记录 | {len(align_rows)} |",
        f"| 补足来源记录 | {len(enr)} |",
        f"| 切段（segments） | {len(seg_rows)} |",
        "",
        "## 迁移说明",
        "",
        "- enrichment 的 field/value 仍为空：字段级内容事实在卡内正文，本轮只记录来源级，深解析留待后续。",
        "- alignment.candidate_id：对 entity-candidates 做名称粗匹配回填，匹配不到者留空（待建候选）。",
        "- 召回率与抽样复核仍待做。",
        "",
    ]
    (RELEASE / "validation-report.md").write_text("\n".join(lines), encoding="utf-8")

    # 汇总
    print(f"ku-manifest: {len(ku_rows)}")
    print(f"relations:   {len(rel_rows)}")
    print(f"candidates:  {len(cand_rows)}")
    print(f"alignment:   {len(align_rows)}")
    print(f"enrichment:  {len(enr)}")
    print(f"segments:    {len(seg_rows)}")
    print(f"tables -> {TABLES}; release -> {RELEASE}")


if __name__ == "__main__":
    main()
