from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
TABLES = ROOT / "04-knowledge" / "tables"
TASK = "s4-s5-s6-zanotti-ch7-ch8-ch14-person-endpoint-20261024"
ANCHOR = TASK
PROCESS_REF = f"03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#{ANCHOR}"
KU = "units/persons/giampietro-zanotti-cavazzoni"
CARD_PATH = "04-knowledge/units/persons/giampietro-zanotti-cavazzoni.md"
CID = "cand-7114"
GROUP = "new-person:giampietro-zanotti-cavazzoni-32c6552065"
SOURCE_ID = "haskell-1980-rev-ed"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)."
)
DATE = "2026-10-24"
TICK = chr(96)


def src(location: str, source_file: str, span: str, summary: str, quote: str) -> dict:
    return {
        "citation": BOOK,
        "location": location,
        "sentence_summary": summary,
        "original_quotes": [{"source_span": span, "text": quote}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": source_file,
            "source_span": span,
        },
    }


SOURCES = [
    src(
        "书后文献表，印刷页441，行1289。",
        "02-sources/02-Markdown/21_CHP-21Bibliography_intro.md",
        "line 1289; print p. 441",
        "Haskell's bibliography lists G. P. Zanotti's two-volume Storia dell’Accademia Clementina, Bologna 1739.",
        "Zanotti, G. P.: Storia dell’Accademia Clementina, 2 vols., Bologna 1739.",
    ),
    src(
        "第14章，印刷页349，注4，行177。",
        "02-sources/02-Markdown/14_CHP-14_intro.md",
        "line 177; print p. 349 n. 4",
        "Haskell attributes a cited letter published in Opere, volume XI, page 213, to G. P. Zanotti; the letter itself was not consulted.",
        "4 Through a letter from G. P. Zanotti of 12 February 1733 published in Opere, XI, p. 213.",
    ),
    src(
        "第8章，印刷页239，注1，行449。",
        "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
        "line 449; print p. 239 n. 1",
        "Haskell interprets Zanotti, volume II, page 54, as implying several Florence visits by Crespi; the cited page was not independently read.",
        "1 L. Crespi, p. 211, says that he was in Florence for two years, whereas it has been shown that during - 1709 he was-there for eight months at most. On the other hand Zanotti, II, p. $4, implies that he went there several times. 2 See p. 237, note 1. —",
    ),
]


def card_bytes() -> bytes:
    title = "吉安彼得罗·扎诺蒂·卡瓦佐尼（Giampietro Zanotti Cavazzoni）"
    fm = {
        "title": title,
        "name_en": "Giampietro Zanotti Cavazzoni",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": SOURCES,
        "created": DATE,
        "updated": DATE,
        "process_ref": PROCESS_REF,
    }
    body = (
        "## 内容\n\n### 描述\n\n"
        "**中文：** 本卡依据既有 S3 跨章身份组，登记哈斯克尔文献表及第7、8、14章中以 G. P. Zanotti／Zanotti 出现的人物。全名扩展沿用既有身份裁决；本卡仅记录哈斯克尔的书目和书信归属，不把所引书页或信件内容写成已独立核实事实。\n\n"
        "**English:** This card registers the person appearing as G. P. Zanotti or Zanotti in Haskell’s bibliography and Chapters 7, 8, and 14, following the existing cross-chapter S3 identity group. The expanded name follows that existing identity decision. This card records Haskell’s bibliographic and letter attributions only; it does not treat the cited pages or letter as independently verified.\n\n"
        "### 身份边界\n\n"
        "本组沿用 `new-person:giampietro-zanotti-cavazzoni-32c6552065`，与 Eustachio Zanotti 保持区分；身份扩展依据及跨章对齐理由见[既有 S3 记录](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-person-giampietro-zanotti-ch7-ch8-ch14-20261024)。本批不重开 S3，也不补写生平。\n\n"
        "This KU follows `new-person:giampietro-zanotti-cavazzoni-32c6552065` and remains distinct from Eustachio Zanotti. The name expansion and cross-chapter alignment are documented in the [existing S3 record](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-person-giampietro-zanotti-ch7-ch8-ch14-20261024). S3 is not reopened in this batch, and no biography is added.\n\n"
        "### 姓名与书内记录\n\n"
        "| 字段 | 值 | 证据 |\n|---|---|---|\n"
        "| 文献表姓名与著作 | Zanotti, G. P.；*Storia dell’Accademia Clementina*, 2 vols., Bologna 1739。 | S1；书后文献表，印刷页441，L1289 |\n"
        "| 书信归属（哈斯克尔注4） | Haskell 将一封刊于 *Opere*, XI, p.213 的书信归于 G. P. Zanotti；书信未独立查阅。 | S2；第14章，印刷页349，注4，L177 |\n\n"
        "### 本书相关内容\n\n"
        "**中文：** 第8章注1把 Zanotti 卷II第54页作为 Haskell 推断 Crespi 曾多次到佛罗伦萨的依据；该页未独立查阅。S2 将此记录为归因性关系候选，S6 本批保留 pending。第14章所引信件的日期在转录与印刷页之间存在已记录的 OCR 校读差异，信件端点仍未完成 S3 身份／粒度裁决。\n\n"
        "**English:** Chapter 8, note 1, cites Zanotti, volume II, page 54, for Haskell’s inference that Crespi visited Florence several times; that page was not independently read. S2 preserves this as an attributed relation candidate and this batch leaves it pending at S6. The date of the letter cited in Chapter 14 has a documented OCR-to-print correction, and the letter endpoint still lacks a settled S3 identity or granularity decision.\n\n"
        "## 关系与证据\n\n### 关系记录\n\n"
        "本批没有新增 formal 关系。两条直接涉及本人物端点的 S2 关系候选及其 pending 理由见[过程记录](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-zanotti-ch7-ch8-ch14-person-endpoint-20261024)。\n\n"
        "### S2 关系候选入口\n\n"
        f"{TICK}st-chp8-p239-note1-zanotti-multiple-visits{TICK}、{TICK}st-chp14-p349-note4-zanotti-letter{TICK}\n"
    )
    fm_text = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000)
    return ("---\n" + fm_text + "---\n\n" + body).encode("utf-8-sig")


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str], bool]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or []), raw.startswith(b"\xef\xbb\xbf")


def csv_bytes(fields: list[str], rows: list[dict[str, str]], bom: bool) -> bytes:
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return (b"\xef\xbb\xbf" if bom else b"") + out.getvalue().encode("utf-8")


def text_bytes(path: Path, text: str) -> bytes:
    bom = path.read_bytes().startswith(b"\xef\xbb\xbf")
    return (b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8")


def replace_once(text: str, before: str, after: str, label: str) -> str:
    n = text.count(before)
    if n != 1:
        raise ValueError(f"expected one baseline for {label}; found {n}")
    return text.replace(before, after, 1)


def update_accepted(text: str) -> str:
    lines = text.splitlines()
    claim_pos = next((i for i, line in enumerate(lines) if line.strip() == "claims:"), None)
    if claim_pos is None:
        raise ValueError("accepted.yml has no units/claims boundary")
    addition = f"- {CARD_PATH}"
    if addition in lines[:claim_pos]:
        raise ValueError("card already appears in accepted.yml")
    insert_at = next(
        (i for i, line in enumerate(lines[:claim_pos])
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_PATH),
        claim_pos,
    )
    lines.insert(insert_at, addition)
    return "\n".join(lines) + "\n"


def build_outputs() -> tuple[dict[Path, bytes], dict[Path, bytes], dict]:
    paths = {
        "alignment": TABLES / "alignment.csv",
        "manifest": TABLES / "ku-manifest.csv",
        "enrichment": TABLES / "enrichment.jsonl",
        "sources": TABLES / "sources.csv",
        "accepted": ROOT / "04-knowledge" / "accepted.yml",
        "statements": TABLES / "book-statements.jsonl",
        "process": ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md",
        "result": ROOT / "04-knowledge" / "results" / "patrons-and-painters-full-book-s2.md",
        "agents": ROOT / "AGENTS.md",
        "card": ROOT / CARD_PATH,
    }
    if any(not path.is_file() for key, path in paths.items() if key != "card"):
        raise FileNotFoundError("a required S4/S5/S6 input is missing")
    alignment, alignment_fields, alignment_bom = read_csv(paths["alignment"])
    manifest, manifest_fields, manifest_bom = read_csv(paths["manifest"])
    sources, _, _ = read_csv(paths["sources"])
    with paths["statements"].open(encoding="utf-8-sig") as handle:
        statements = [json.loads(line) for line in handle if line.strip()]
    with paths["enrichment"].open(encoding="utf-8-sig") as handle:
        enrichment = [json.loads(line) for line in handle if line.strip()]
    accepted_text = paths["accepted"].read_text(encoding="utf-8-sig")
    process_text = paths["process"].read_text(encoding="utf-8-sig")
    result_text = paths["result"].read_text(encoding="utf-8-sig")
    agents_text = paths["agents"].read_text(encoding="utf-8-sig")
    if len(statements) != 15333 or sum(s.get("qualifiers", {}).get("relation_candidate") is True for s in statements) != 10547:
        raise ValueError("S2/S6 baseline changed; re-audit before this batch")
    if ANCHOR in process_text or paths["card"].exists() or CARD_PATH in accepted_text:
        raise ValueError("this S4 batch already appears in current data")
    if not any(row.get("source_id") == SOURCE_ID for row in sources):
        raise ValueError(f"missing source registry entry {SOURCE_ID}")

    primary = [r for r in alignment if r.get("candidate_id") and not r.get("external_source") and not r.get("external_id")]
    matches = [r for r in primary if r.get("candidate_id") == CID]
    if len(matches) != 1:
        raise ValueError(f"expected one primary alignment row for {CID}; found {len(matches)}")
    chosen = matches[0]
    if chosen.get("decision") != "new" or chosen.get("ku_id") or GROUP not in chosen.get("resolution_note", ""):
        raise ValueError("Zanotti S3 decision/group is no longer the expected unresolved new group")
    if any(r.get("ku_id") == KU or r.get("card_path") == CARD_PATH for r in manifest):
        raise ValueError("Zanotti KU already exists in manifest")
    if any(r.get("type") == "person" and r.get("name_en", "").casefold() == "giampietro zanotti cavazzoni" for r in manifest):
        raise ValueError("possible person identity collision in manifest")
    other = {r.get("candidate_id"): r for r in primary}
    if other.get("cand-10262", {}).get("decision") != "undecided":
        raise ValueError("the cited letter endpoint has changed; reassess S6 decision")
    if other.get("cand-0871", {}).get("ku_id") != "units/persons/giuseppe-maria-crespi":
        raise ValueError("the Crespi endpoint has changed; reassess S6 decision")

    target_sids = {
        "st-chp8-p239-note1-zanotti-multiple-visits",
        "st-chp14-p349-note4-zanotti-letter",
    }
    statement_by_id = {s["statement_id"]: s for s in statements}
    if len(statement_by_id) != len(statements):
        raise ValueError("duplicate S2 statement IDs")
    for sid in target_sids:
        s = statement_by_id.get(sid)
        if not s or s.get("qualifiers", {}).get("relation_candidate") is not True or CID not in {
            s.get("subject_candidate_id"), s.get("object_candidate_id")
        }:
            raise ValueError(f"missing direct S6 candidate or endpoint: {sid}")
        if re.search(rf"(?m)^\|\s*{re.escape(TICK + sid + TICK)}\s*\|\s*(formal|pending|rejected)\s*\|", process_text):
            raise ValueError(f"an S6 disposition already exists for {sid}")

    card = card_bytes()
    alignment_after = [dict(r) for r in alignment]
    for row in alignment_after:
        if row.get("alignment_id") == chosen.get("alignment_id"):
            row["ku_id"] = KU
            row["process_ref"] = PROCESS_REF
            row["resolution_note"] += (
                f" S4 registration: mapped existing S3 group {GROUP} to {KU}; "
                "uses Haskell's cross-chapter name forms and bibliographic context; no new S3 decision or biography is added."
            )
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU,
        "type": "person",
        "canonical_name": "吉安彼得罗·扎诺蒂·卡瓦佐尼（Giampietro Zanotti Cavazzoni）",
        "name_en": "Giampietro Zanotti Cavazzoni",
        "source_task": TASK,
        "card_path": CARD_PATH,
    })
    accepted_after = update_accepted(accepted_text)

    from scripts import build_field_facts as field_facts
    original_base = field_facts.BASE
    try:
        with tempfile.TemporaryDirectory(prefix="pnp-zanotti-preview-") as temp_dir:
            temp_root = Path(temp_dir)
            temp_card = temp_root / CARD_PATH
            temp_card.parent.mkdir(parents=True, exist_ok=True)
            temp_card.write_bytes(card)
            field_facts.BASE = temp_root
            fields, source_registry, warnings, cards_with_tables = field_facts.extract_records([planned_manifest[-1]])
    finally:
        field_facts.BASE = original_base
    if warnings or cards_with_tables != 1 or len(fields) != 2:
        raise ValueError(f"S5 extraction mismatch: cards={cards_with_tables}; fields={len(fields)}; warnings={warnings}")
    field_facts.assign_ids(fields, paths["enrichment"])
    if any(r.get("source_ids") != [SOURCE_ID] or r.get("evidence_status") != "source_backed" for r in fields):
        raise ValueError("one or more S5 rows lacks Haskell source support")
    if source_registry.keys() != {SOURCE_ID}:
        raise ValueError(f"unexpected source registry keys from card: {sorted(source_registry)}")

    all_ids = {r["candidate_id"] for r in primary}
    if len(all_ids) != len(primary):
        raise ValueError("primary S3 candidate rows are not unique")
    endpoint_ids = set()
    for statement in statements:
        if statement.get("qualifiers", {}).get("relation_candidate") is True:
            endpoint_ids.update(cid for cid in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")) if cid)
    new_total = sum(r.get("decision") == "new" for r in primary)
    mapped_before = sum(r.get("decision") == "new" and bool(r.get("ku_id")) for r in primary)
    endpoint_pending_before = sum(
        r["candidate_id"] in endpoint_ids and r.get("decision") == "new" and not r.get("ku_id")
        for r in primary
    )
    if mapped_before != 2031 or new_total != 5071 or endpoint_pending_before != 1320:
        raise ValueError(f"S4 baseline differs from live row count: mapped={mapped_before}, new={new_total}, direct_pending={endpoint_pending_before}")
    s4_mapped = mapped_before + 1
    s4_pending = new_total - s4_mapped
    s4_direct_pending = endpoint_pending_before - 1
    s5_total = len(enrichment) + len(fields)
    if len(enrichment) != 13141 or s5_total != 13143:
        raise ValueError(f"unexpected S5 baseline/total: {len(enrichment)} -> {s5_total}")

    process_note = (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n"
        f"### 第7、8、14章 Giampietro Zanotti 跨章人物端点登记及 S6 裁决（{DATE}）\n\n"
        "#### S3 身份组与 S4 登记\n\n"
        f"沿用既有 S3 决定：`{CID}` 属于 `{GROUP}`，跨第7章 pp.189、192、194，第8章 pp.223–225、239及第14章 p.349；"
        f"映射至 `{KU}`。本批不重开 S3，不把 Zanotti 与其子 Eustachio 合并；书名及身份理由见既有 S3 记录。\n\n"
        "#### S5 来源字段\n\n"
        f"新增 {len(fields)} 条 Haskell 来源、`source_backed` 字段：文献表所列署名与著作，以及第14章注4的书信归属。"
        "S2 转录将日期 OCR 为1733，打印页核读为1735；本批保留这一来源校读边界，不声称查阅过所引信件。\n\n"
        "#### S6 逐项裁决\n\n"
        "两条直接使用 Zanotti 为关系端点的 S2 候选均记为 pending；未新增 formal 关系行。\n\n"
        "| statement_id | status | decision / evidence boundary |\n|---|---|---|\n"
        "| `st-chp8-p239-note1-zanotti-multiple-visits` | pending | 这是 Haskell 对未独立查阅的 Zanotti II, p.54 的归因性解释，不是可直接表达的 Zanotti→Crespi 受控关系；保留原书判断，不把它改写为历史关系。 |\n"
        "| `st-chp14-p349-note4-zanotti-letter` | pending | `authored_by` 类型可表达 archive→person，但信件候选 `cand-10262` 仍为 S3 undecided，身份／粒度端点未解决；S3 决定后再评估正式边。原 OCR 的1733与打印页1735差异照实保留。 |\n\n"
        "本批不改 S2 statement、mention 或独立复核分子；两条 pending 的解除条件分别是关系语义可由受控类型表达，以及 `cand-10262` 的 S3 身份／粒度得到证据支持。"
    )
    process_after = process_text.rstrip() + process_note + "\n"

    summary = (
        f"**第7、8、14章 Zanotti 人物端点批次（{DATE}）：** 沿用既有 S3 跨章 new 组 `{CID}`，"
        f"登记1个 person KU 并映射1条候选；新增{len(fields)}条 Haskell `source_backed` S5 字段。"
        "两条直接 S6 候选均 pending：一条是 Haskell 对未读 Zanotti 页的归因性解释，另一条受制于未决信件端点；未新增 formal 边。"
        "S2 statement、mention和独立复核分子不变。详见"
        f"[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#{ANCHOR})。"
    )
    result_marker = "### 本轮进度与后续工作（2026-10-24）"
    if result_text.count(result_marker) != 1:
        raise ValueError("current result marker changed")
    result_after = result_text.replace(result_marker, result_marker + "\n\n" + summary, 1)
    # Refresh the live snapshot and the plan's mirrored stage totals.
    replacements = [
        ("S4已映射2,031/5,071条new候选，待登记3,040条，其中1,322条触及关系端点；当前KU共2,818个。", f"S4已映射{s4_mapped:,}/5,071条new候选，待登记{s4_pending:,}条，其中{s4_direct_pending:,}条触及关系端点；当前KU共2,819个。"),
        ("S5字段13,141条，1,634条unverified。", f"S5字段{s5_total:,}条，1,634条unverified。"),
        ("累计逐项裁决1,180条（676 formal、397 pending、107 rejected），尚有9,367条未裁决。", "累计逐项裁决1,182条（676 formal、399 pending、107 rejected），尚有9,365条未裁决。"),
        ("另有1,370个孤立KU", "另有1,371个孤立KU"),
        ("S4已映射2,031/5,071条new候选，待映射3,040条，其中1,322条触及关系端点。", f"S4已映射{s4_mapped:,}/5,071条new候选，待映射{s4_pending:,}条，其中{s4_direct_pending:,}条触及关系端点。"),
        ("S4已映射2,031/5,071条new候选，待映射3,040条，其中1,322条触及关系端点；", f"S4已映射{s4_mapped:,}/5,071条new候选，待映射{s4_pending:,}条，其中{s4_direct_pending:,}条触及关系端点；"),
        ("S5有13,141条字段、1,634条unverified", f"S5有{s5_total:,}条字段、1,634条unverified"),
        ("S6已逐项裁决1,180/10,547条，尚余9,367条", "S6已逐项裁决1,182/10,547条，尚余9,365条"),
        ("对暂记9,617条逐项对到当前statement ID", "对暂记9,617条逐项对到当前statement ID"),
        ("S6余下9,367条按端点齐备", "S6余下9,365条按端点齐备"),
    ]
    for before, after in replacements:
        if before in result_after:
            result_after = result_after.replace(before, after)
    agents_after = replace_once(agents_text, "S4已映射2,031/5,071条new候选，待映射3,040条，其中1,322条触及关系端点。", f"S4已映射{s4_mapped:,}/5,071条new候选，待映射{s4_pending:,}条，其中{s4_direct_pending:,}条触及关系端点。", "AGENTS S4")
    agents_after = replace_once(agents_after, "S5字段13,141条（1,634条unverified）。", f"S5字段{s5_total:,}条（1,634条unverified）。", "AGENTS S5")
    agents_after = replace_once(agents_after, "S6已裁决1,180/10,547条（676 formal、397 pending、107 rejected），尚余9,367条；", "S6已裁决1,182/10,547条（676 formal、399 pending、107 rejected），尚余9,365条；", "AGENTS S6")

    enr_raw = paths["enrichment"].read_bytes()
    ending = b"" if enr_raw.endswith((b"\n", b"\r")) else b"\n"
    enr_after = enr_raw + ending + b"".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n" for r in fields)
    output = {
        paths["alignment"]: csv_bytes(alignment_fields, alignment_after, alignment_bom),
        paths["manifest"]: csv_bytes(manifest_fields, planned_manifest, manifest_bom),
        paths["enrichment"]: enr_after,
        paths["accepted"]: text_bytes(paths["accepted"], accepted_after),
        paths["process"]: text_bytes(paths["process"], process_after),
        paths["result"]: text_bytes(paths["result"], result_after),
        paths["agents"]: text_bytes(paths["agents"], agents_after),
        paths["card"]: card,
    }
    before = {p: p.read_bytes() for p in output if p.exists()}
    meta = {
        "candidate_id": CID,
        "s3_group": GROUP,
        "new_ku": KU,
        "new_fields": len(fields),
        "s2_statements": len(statements),
        "s2_relation_candidates": sum(s.get("qualifiers", {}).get("relation_candidate") is True for s in statements),
        "s4_total_mapped": s4_mapped,
        "s4_total_pending": s4_pending,
        "s4_direct_endpoint_pending": s4_direct_pending,
        "s5_total_fields": s5_total,
        "s6_total_decided": 1182,
        "s6_total_pending": 399,
        "s6_total_undecided": 9365,
        "new_s6_dispositions": {sid: "pending" for sid in sorted(target_sids)},
        "touched_files": [p.relative_to(ROOT).as_posix() for p in output],
        "output_sha256": {p.relative_to(ROOT).as_posix(): hashlib.sha256(b).hexdigest() for p, b in output.items()},
    }
    return output, before, meta


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    output, before, meta = build_outputs()
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    if not args.apply:
        print("dry-run only; no project files written")
        return 0
    recovery = ROOT / "06-runtime" / "recovery" / "S4-S5-S6-Zanotti-ch7-ch8-ch14-2026-10-24"
    if recovery.exists():
        raise FileExistsError(f"recovery directory already exists: {recovery}")
    recovery.mkdir(parents=True)
    backup_manifest = {}
    for path in output:
        rel = path.relative_to(ROOT).as_posix()
        if path not in before:
            backup_manifest[rel] = None
            continue
        backup = recovery / "original" / rel
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_bytes(before[path])
        backup_manifest[rel] = hashlib.sha256(before[path]).hexdigest()
    (recovery / "backup-manifest.json").write_text(json.dumps(backup_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    written = []
    try:
        for path, content in output.items():
            with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
                handle.write(content)
                temp_path = Path(handle.name)
            temp_path.replace(path)
            written.append(path)
            if hashlib.sha256(path.read_bytes()).hexdigest() != hashlib.sha256(content).hexdigest():
                raise RuntimeError(f"post-write verification failed: {path.relative_to(ROOT)}")
    except Exception:
        for path in reversed(written):
            if path in before:
                path.write_bytes(before[path])
            elif path.exists():
                path.unlink()
        raise
    print(f"apply complete: {len(written)} files; recovery copy: {recovery.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
