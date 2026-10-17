from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
from collections import Counter
from pathlib import Path


ROOT = Path.cwd()
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
RESULT = ROOT / "04-knowledge" / "results" / "patrons-and-painters-full-book-s2.md"
KNOWLEDGE = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
PROCESS_REF = "S3-full-book-2026-10-16"
GROUP = "archive-group-ff938f5595f2"


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bool]:
    raw = path.read_bytes()
    had_bom = raw.startswith(b"\xef\xbb\xbf")
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader), had_bom


def encode_csv(headers: list[str], rows: list[dict[str, str]], had_bom: bool) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=headers, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    text = stream.getvalue()
    return ("\ufeff" + text if had_bom else text).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not (ROOT / "04-knowledge" / "accepted.yml").exists():
        raise SystemExit("Run this script from the project root.")

    alignment_headers, alignment, alignment_bom = read_csv(ALIGNMENT)
    _, candidate_rows, _ = read_csv(CANDIDATES)
    candidates = {row["candidate_id"]: row for row in candidate_rows}
    primary = [row for row in alignment if not row["external_source"]]
    external = [row for row in alignment if row["external_source"]]
    primary_by_id = {row["candidate_id"]: row for row in primary}
    expected = Counter({"same": 1768, "new": 5012, "undecided": 5517, "excluded": 99, "conflict": 8})
    if len(primary) != 12404 or len(alignment) != 12619 or len(external) != 215 or Counter(row["decision"] for row in primary) != expected:
        raise SystemExit("Unexpected S3 baseline; inspect before changing the candidate.")

    index_candidate = candidates.get("cand-1532")
    archive_candidate = candidates.get("cand-5338")
    work_candidate = candidates.get("cand-11509")
    index_decision = primary_by_id.get("cand-1532")
    archive_decision = primary_by_id.get("cand-5338")
    work_decision = primary_by_id.get("cand-11509")
    if not index_candidate or (index_candidate["suggested_type"], index_candidate["index_entry_id"], index_candidate["sub_entry"], index_candidate["index_page_range"]) != ("archive", "M.csv#69", "documents relating to S. Andrea al Quirinale altarpieces", "386, 387"):
        raise SystemExit("cand-1532 index identity changed.")
    if not index_decision or index_decision["decision"] != "undecided" or index_decision["ku_id"]:
        raise SystemExit("cand-1532 is no longer the expected undecided candidate.")
    if not archive_candidate or archive_candidate["suggested_type"] != "archive" or not archive_decision or archive_decision["decision"] != "new" or f"group={GROUP}" not in archive_decision["resolution_note"] or archive_decision["ku_id"]:
        raise SystemExit("cand-5338 is no longer in the expected pending archive group.")
    if not work_candidate or work_candidate["suggested_type"] != "work" or not work_decision or work_decision["decision"] != "undecided":
        raise SystemExit("The separate altarpiece-work group changed; inspect before applying.")

    with MENTIONS.open("r", encoding="utf-8-sig", newline="") as stream:
        mentions = {row["mention_id"]: row for row in csv.DictReader(stream)}
    if mentions.get("m-chp19-p386-006", {}).get("candidate_id") != "cand-5338":
        raise SystemExit("The Appendix 1 archival locator no longer points to cand-5338.")
    if not any(row.get("note") == "Reuse the existing archive candidate." for row in mentions.values() if row.get("candidate_id") == "cand-5338"):
        raise SystemExit("The Chapter 3 N. 865-13 reuses are no longer mapped to cand-5338.")
    with STATEMENTS.open("r", encoding="utf-8-sig") as stream:
        statements = [json.loads(line) for line in stream if line.strip()]
    by_statement = {row["statement_id"]: row for row in statements}
    expected_statements = {
        "st-chp19-p386-appendix-archive-locator",
        "st-chp3-seciv-notes-l205-243-p88-n2-86513",
        "st-chp3-seciv-notes-l205-243-p88-n3-86513",
    }
    if not expected_statements.issubset(by_statement):
        raise SystemExit("The cross-chapter N. 865-13 source statements changed.")
    appendix = by_statement["st-chp19-p386-appendix-archive-locator"].get("qualifiers", {}).get("claim", "")
    if "Fondo di Gesù N. 865-13" not in appendix or "altarpieces" not in appendix.casefold():
        raise SystemExit("The Appendix 1 heading no longer provides the matching archive locator and subject.")

    prior_note = index_decision["resolution_note"]
    updated = [dict(row) for row in alignment]
    by_id = {row["candidate_id"]: row for row in updated if not row["external_source"]}
    by_id["cand-1532"].update(
        decision="new",
        process_ref=PROCESS_REF,
        resolution_note=(
            "source_ref=index_entry=M.csv#69;pages=386,387; body_archive_candidate=cand-5338; "
            "mentions=m-chp19-p386-005,m-chp19-p386-006; "
            "statements=st-chp19-p386-appendix-archive-locator,st-chp3-seciv-notes-l205-243-p88-n2-86513,st-chp3-seciv-notes-l205-243-p88-n3-86513; "
            f"identity_peer=cand-5338; group={GROUP}. The Appendix 1 heading identifies the material as documents about the S. Andrea al Quirinale altarpieces by Giacinto Brandi and Carlo Maratta in Jesuit Archives, Fondo di Gesù N. 865-13; ch.3 pp.87-88 notes cite the same fonds/item and direct readers to Appendix 1. "
            "The index slice and the body archive candidate therefore identify the same archival file/dossier and remain in one pending new archive group. Keep separate from the work candidates for individual/unnamed altarpieces, including cand-11509, and do not treat the file as one painting. The archive record itself was not independently consulted. "
            f"prior_resolution_note={prior_note}"
        ),
    )

    result_text = RESULT.read_text(encoding="utf-8-sig")
    replacements = [
        ("new=5,012（4,833个身份组）", "new=5,013（4,833个身份组）"),
        ("undecided=5,517。S4 已登记281组、映射352条成员候选；尚待登记4,552组、4,660条映射。", "undecided=5,516。S4 已登记281组、映射352条成员候选；尚待登记4,552组、4,661条映射。"),
        ("| new | 5,012 | 按 4,833 个当前身份组进入 S4；每组登记一个 KU |", "| new | 5,013 | 按 4,833 个当前身份组进入 S4；每组登记一个 KU |"),
        ("| undecided | 5,517 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |", "| undecided | 5,516 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |"),
        ("| archive | 79→61 | 1,253／1,217 | 29／1,188；1,218 | 0 | 18 | 750 |", "| archive | 79→61 | 1,254／1,217 | 29／1,188；1,219 | 0 | 18 | 749 |"),
        ("| **合计** | **1,768→1,026** | **5,012／4,833** | **281／4,552；4,660** | **8** | **99** | **5,517** |", "| **合计** | **1,768→1,026** | **5,013／4,833** | **281／4,552；4,661** | **8** | **99** | **5,516** |"),
    ]
    for old, new in replacements:
        if result_text.count(old) != 1:
            raise SystemExit(f"Expected one result occurrence of {old!r}, found {result_text.count(old)}")
        result_text = result_text.replace(old, new, 1)
    section = (
        "### S3 archive：S. Andrea al Quirinale N. 865-13 索引候选并入档案组（2026-10-16）\n\n"
        f"- `cand-1532`（M.csv#69，pp.386–387）由 `undecided` 改为 `new`，与 `cand-5338` 同入 `{GROUP}`，待 S4 登记一个 archive KU。附录1说明该档案项为有关 Brandi、Maratta 在 S. Andrea al Quirinale 祭坛画的文件，定位于耶稣档案馆 Fondo di Gesù N.865-13；第3章注2、注3引同一编号并交叉指向附录1。\n"
        "- 档案项/文件组与作品候选分开：不将目录组当成一幅画，也不据此判定未具名祭坛画的数量、标题或完成状态。档案原件未独立查阅，未新建 KU 或关系。"
    )
    marker = "### S4 按类型登记进度"
    if result_text.count(marker) != 1:
        raise SystemExit("Could not find the S4 type-progress insertion point.")
    result_text = result_text.replace(marker, section + "\n\n" + marker, 1)

    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    knowledge_text += (
        "\n\n### S3 archive：S. Andrea al Quirinale N. 865-13 索引候选并入档案组（2026-10-16）\n\n"
        f"- `cand-1532`（M.csv#69，pp.386–387）从 `undecided` 改为 `new`，与 `cand-5338` 同属 `{GROUP}`。附录1 p.386 的 locator statement `st-chp19-p386-appendix-archive-locator` 明载关于 S. Andrea al Quirinale 的 Brandi、Maratta 祭坛画文件，地址为 Jesuit Archives, Fondo di Gesù—N.865-13；第3章 p.88 注2、注3 statements `st-chp3-seciv-notes-l205-243-p88-n2-86513` 与 `...-n3-86513` 复用同一 callmark 并分别指向 Appendix 1 中 Brandi 书信与 Maratta 相关材料。索引子项、档案编号和正文交叉引用共同表明这是一份档案项目/文件组的同一 identity group。\n"
        "- `cand-11509` 是有关祭坛画的 work 候选，仍保持 undecided；N.865-13 文件组不等同于其中任一绘画，也不证明全部计划作品均已完成。档案原件没有独立查阅；本轮只裁决档案对象身份，不登记 KU、卡片或正式关系。"
    )

    updates = {
        ALIGNMENT: encode_csv(alignment_headers, updated, alignment_bom),
        RESULT: ("\ufeff" + result_text).encode("utf-8"),
        KNOWLEDGE: ("\ufeff" + knowledge_text).encode("utf-8"),
    }
    print("PREVIEW" if not args.apply else "APPLY")
    for path, content in updates.items():
        print(f"  {path.relative_to(ROOT)}: {sha256(path.read_bytes())} -> {sha256(content)}")
    print("  S3 decisions:", dict(Counter(row["decision"] for row in primary)), "->", dict(Counter(row["decision"] for row in updated if not row["external_source"])))
    print(f"  identity group: cand-1532 + cand-5338 -> {GROUP}; group count unchanged, pending member mappings +1; cand-11509 remains undecided")
    if not args.apply:
        print("Dry-run only; pass --apply to write the changes.")
        return

    for path in updates:
        backup = path.with_name(path.name + ".bak-s3-jesuit-archive-86513-20261016")
        if backup.exists():
            raise SystemExit(f"Recovery copy already exists: {backup}")
        shutil.copy2(path, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s3-jesuit-archive-86513-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied the archive identity grouping and retained recovery copies.")


if __name__ == "__main__":
    main()
