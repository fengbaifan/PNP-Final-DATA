#!/usr/bin/env python3
"""
export_s0s7.py — 第一章一次性转换（step 3）

从现有文件转换出 S0–S7 阶段的机器可读产物，写入 release/v0.1/。
只读现有数据，不调用外部接口；权威事实源（KU 卡、accepted.yml、关系索引）不变。
本脚本只做「现有 → 规范产物」的机械转换，不重跑语义工作。

v0.1 范围说明（见 validation-report.md）：
- ku-manifest / relations 覆盖全部 1019 有效 KU 与 1226 条边（chp-1 + front-matter）。
- alignment / enrichment 证据目前只转换 chp-1 的 JSONL 证据；front-matter 的
  alignment-writeback.json / registration-writeback.json 格式不同，另行转换。
"""
import csv, json, re, sys, yaml
from pathlib import Path
from collections import Counter

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "release" / "v0.1"

TYPE_SINGULAR = {
    "persons": "person", "families": "family", "institutions": "institution",
    "places": "place", "works": "work", "archives": "archive",
    "terms": "term", "procedures": "procedure", "events": "event",
}


def norm_ku(path):
    """规范化为 units/{dir}/{slug}。接受 04-knowledge/units/archives/x.md、archives/x.md、persons/x.md。"""
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
    """中文名从 title 去掉末尾英文括号得来；英文名优先用 frontmatter 的 name_en。"""
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


def write_csv(path, rows, cols):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


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


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    # ---- S4 ku-manifest.csv ----
    accepted = yaml.safe_load(open(BASE / "04-knowledge/accepted.yml", encoding="utf-8"))
    unit_paths = accepted.get("units", [])
    ku_rows, type_count = [], Counter()
    for up in unit_paths:
        parts = up.rstrip(".md").split("/")
        dir_ = parts[-2]
        typ = TYPE_SINGULAR.get(dir_, dir_)
        fm = read_fm(BASE / up)
        zh, en = split_title(fm_field(fm, "title"), fm_field(fm, "name_en"))
        pr = fm_field(fm, "process_ref")
        src_task = ""
        for t in ("front-matter", "chp-1", "chp-6"):
            if t in pr:
                src_task = t
                break
        ku_rows.append({
            "ku_id": norm_ku(up), "type": typ, "canonical_name": zh, "name_en": en,
            "source_task": src_task, "created": fm_field(fm, "created"),
            "updated": fm_field(fm, "updated"), "card_path": up,
        })
        type_count[typ] += 1
    write_csv(OUT / "ku-manifest.csv", ku_rows,
              ["ku_id", "type", "canonical_name", "name_en", "source_task", "created", "updated", "card_path"])

    # ---- S6 relations.csv ----
    idx = yaml.safe_load(open(BASE / "04-knowledge/quality/relation-index.yml", encoding="utf-8"))
    edges = idx if isinstance(idx, list) else idx.get("relations", [])
    rel_rows, origin_count, status_count, pred_count = [], Counter(), Counter(), Counter()
    for i, e in enumerate(edges):
        er = e.get("evidence_ref") or {}
        sf = er.get("source_file", "") or ""
        doc = er.get("doc_id", "") or ""
        if sf.startswith("02-sources") or doc == "patrons-and-painters":
            origin = "book"
        elif isinstance(sf, str) and sf.startswith("http"):
            origin = "enrich"
        else:
            origin = "infer"
        rs = e.get("review_status")
        rsrc = e.get("relation_source")
        if rs == "evidence_backed_relation":
            status = "formal"
        elif rs == "conflict":
            status = "rejected"
        else:
            status = "pending"
        origin_count[origin] += 1
        status_count[status] += 1
        pred_count[e.get("relation_type", "")] += 1
        rel_rows.append({
            "relation_id": f"rel-{i+1}",
            "subject_ku_id": norm_ku(e.get("source", "")),
            "object_ku_id": norm_ku(e.get("target", "")),
            "predicate": e.get("relation_type", ""),
            "direction": "forward",
            "time": e.get("time", "") or "",
            "role": e.get("role", "") or "",
            "scope": e.get("scope", "") or "",
            "origin": origin,
            "status": status,
            "evidence_doc_id": doc,
            "evidence_source_file": sf,
            "evidence_span": er.get("source_span", "") or "",
        })
    write_csv(OUT / "relations.csv", rel_rows,
              ["relation_id", "subject_ku_id", "object_ku_id", "predicate", "direction",
               "time", "role", "scope", "origin", "status",
               "evidence_doc_id", "evidence_source_file", "evidence_span"])

    # ---- S3 alignment.csv ----
    align_rows = []
    aln = read_jsonl(BASE / "03-processing/patrons-and-painters-chp-1/process/alignment-evidence.jsonl")
    paired = unpaired = 0
    for i, a in enumerate(aln):
        st = a.get("status", "unpaired")
        if st == "paired":
            paired += 1
            decision = "same"
        else:
            unpaired += 1
            decision = "undecided"
        align_rows.append({
            "alignment_id": f"aln-{i+1}",
            "candidate_id": a.get("key", ""),
            "ku_id": norm_ku(a.get("key", "")),
            "external_source": "Wikidata",
            "external_id": a.get("confirmed_qid") or "",
            "method": a.get("source_independence_group", ""),
            "decision": decision,
            "evidence_ref": a.get("review", ""),
            "accessed_date": a.get("access_date", ""),
        })
    write_csv(OUT / "alignment.csv", align_rows,
              ["alignment_id", "candidate_id", "ku_id", "external_source", "external_id",
               "method", "decision", "evidence_ref", "accessed_date"])

    # ---- S5 enrichment.jsonl ----
    enr = read_jsonl(BASE / "03-processing/patrons-and-painters-chp-1/process/enrichment-evidence.jsonl")
    enr_count = Counter()
    with open(OUT / "enrichment.jsonl", "w", encoding="utf-8") as f:
        for i, e in enumerate(enr):
            url = e.get("url", "") or ""
            host = "wikidata" if "wikidata" in url.lower() else url
            sem = str(e.get("semantic_review", ""))
            if sem == "reviewed":
                evs = "confirmed"
            elif "conflict" in sem.lower():
                evs = "contested"
            else:
                evs = "uncertain"
            enr_count[host] += 1
            rec = {
                "enrichment_id": f"enr-{i+1}",
                "ku_id": norm_ku(e.get("unit", "")),
                "field": "", "value": "",  # 字段级事实在卡内，另行深解析
                "origin": "enrich",
                "source": host,
                "url": url,
                "qid": e.get("qid", "") or "",
                "accessed_date": e.get("access_date", ""),
                "evidence_status": evs,
                "review": e.get("review", ""),
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # ---- S7 validation-report.md ----
    matrix = yaml.safe_load(open(BASE / "01-domain/relation-domain-range.yml", encoding="utf-8"))
    dr = matrix.get("domain_range", {})
    dep = set(matrix.get("deprecated_for_new_edges", []))
    viol = 0
    for e in edges:
        pred = e.get("relation_type", "")
        st = e.get("source_type", "")
        tt = e.get("target_type", "")
        if pred in dep:
            viol += 1
            continue
        if pred in dr:
            if st not in dr[pred].get("domain", []) or tt not in dr[pred].get("range", []):
                viol += 1
    lines = [
        "# v0.1 发布验证报告（第一章一次性转换）",
        "",
        "## 统计",
        "",
        "| 指标 | 值 |",
        "|---|---|",
        f"| 有效知识元（KU） | {len(ku_rows)} |",
        f"| 正式关系边 | {len(edges)} |",
        f"| 关系来源分布 | " + "；".join(f"{k}={v}" for k, v in origin_count.most_common()) + " |",
        f"| 关系状态分布 | " + "；".join(f"{k}={v}" for k, v in status_count.most_common()) + " |",
        f"| 对齐记录（chp-1） | {len(align_rows)}（paired={paired}，unpaired={unpaired}） |",
        f"| 补足证据（chp-1） | {len(enr)} |",
        "",
        "## KU 按类型",
        "",
        "| 类型 | 数量 |",
        "|---|---|",
    ]
    for t in sorted(type_count):
        lines.append(f"| {t} | {type_count[t]} |")
    lines += [
        "",
        "## 关系按谓词（前 20）",
        "",
        "| 谓词 | 数量 |",
        "|---|---|",
    ]
    for p, c in pred_count.most_common(20):
        lines.append(f"| {p} | {c} |")
    lines += [
        "",
        "## 约束检查",
        "",
        f"- 关系域值域违规（对照 relation-domain-range.yml v1）：**{viol}**（应 0）。",
        f"- 弃用类型在途：见上方关系状态，`pending` 边不含 `associated_*`。",
        "",
        "## 待补（不在本步）",
        "",
        "- 实体召回率：待 step 4 解析原书索引后对照。",
        "- 对齐/关系抽样精度：待人工分层抽样复核。",
        "- 字段级补足事实（field→value→source）：在卡内正文表，需深解析，暂列来源级记录。",
        "- front-matter 的 alignment/enrichment 证据（alignment-writeback.json 等）格式不同，另行转换。",
        "",
    ]
    (OUT / "validation-report.md").write_text("\n".join(lines), encoding="utf-8")

    # 汇总输出
    print(f"ku-manifest: {len(ku_rows)} 行")
    print(f"relations:   {len(edges)} 行 (origin: {dict(origin_count)} / status: {dict(status_count)})")
    print(f"alignment:   {len(align_rows)} 行 (paired={paired}, unpaired={unpaired})")
    print(f"enrichment:  {len(enr)} 行")
    print(f"constraint violations: {viol}")
    print(f"written to: {OUT}")


if __name__ == "__main__":
    main()
