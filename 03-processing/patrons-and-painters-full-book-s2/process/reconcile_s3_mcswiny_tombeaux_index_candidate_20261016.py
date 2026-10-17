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
MANIFEST = TABLES / "ku-manifest.csv"
RESULT = ROOT / "04-knowledge" / "results" / "patrons-and-painters-full-book-s2.md"
KNOWLEDGE = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
PROCESS_REF = "S3-full-book-2026-10-16"
GROUP = "archive-group-25725e686a64"


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
    _, candidates_rows, _ = read_csv(CANDIDATES)
    candidates = {row["candidate_id"]: row for row in candidates_rows}
    primary = [row for row in alignment if not row["external_source"]]
    external = [row for row in alignment if row["external_source"]]
    primary_by_id = {row["candidate_id"]: row for row in primary}
    if len(primary) != 12404 or len(alignment) != 12618 or len(external) != 214:
        raise SystemExit("Unexpected alignment shape; inspect the current S3 baseline.")
    expected = Counter({"same": 1767, "new": 5006, "undecided": 5524, "excluded": 99, "conflict": 8})
    if Counter(row["decision"] for row in primary) != expected:
        raise SystemExit("Unexpected S3 decisions; inspect the current baseline.")

    index_candidate = candidates.get("cand-1474")
    body_candidate = candidates.get("cand-9032")
    if not index_candidate or (index_candidate["index_entry_id"], index_candidate["sub_entry"], index_candidate["suggested_type"]) != ("M.csv#11", "Tombeaux des Princes", "archive"):
        raise SystemExit("cand-1474 no longer identifies the expected archive index entry.")
    if not body_candidate or body_candidate["suggested_type"] != "archive":
        raise SystemExit("cand-9032 is missing or no longer has archive type.")
    index_decision = primary_by_id["cand-1474"]
    body_decision = primary_by_id["cand-9032"]
    if index_decision["decision"] != "undecided" or index_decision["ku_id"]:
        raise SystemExit("cand-1474 is no longer the expected undecided candidate.")
    if body_decision["decision"] != "new" or f"group={GROUP}" not in body_decision["resolution_note"]:
        raise SystemExit("cand-9032 is no longer in the expected pending new archive group.")
    if any(row["candidate_id"] == "cand-1474" and row["external_source"] for row in alignment):
        raise SystemExit("cand-1474 already has an external identity record; review before changing it.")
    if "Tombeaux des Princes" not in body_candidate["canonical_name"] or "1741" not in body_candidate["canonical_name"]:
        raise SystemExit("cand-9032 title/year identity anchor changed.")

    with MENTIONS.open("r", encoding="utf-8-sig", newline="") as stream:
        mentions = {row["mention_id"]: row for row in csv.DictReader(stream)}
    expected_mentions = {"m-chp10-p291-published-volume-title", "m-chp10-p289-note2-tombeaux"}
    if any(mentions.get(mid, {}).get("candidate_id") != "cand-9032" for mid in expected_mentions):
        raise SystemExit("The S2 title/page anchors for cand-9032 changed.")
    with STATEMENTS.open("r", encoding="utf-8-sig") as stream:
        statements = [json.loads(line) for line in stream if line.strip()]
    expected_statements = {
        "st-chp10-p289-note2-1741-publication",
        "st-chp10-p291-volume-publication-and-disappointment",
        "st-chp10-p291-volume-plate-and-tomb-count",
    }
    statement_by_id = {row["statement_id"]: row for row in statements}
    if not expected_statements.issubset(statement_by_id):
        raise SystemExit("Expected publication statements for the 1741 volume are missing.")
    if any("cand-9032" not in statement_by_id[sid].get("qualifiers", {}).get("mentioned_candidate_ids", []) for sid in expected_statements):
        raise SystemExit("The publication statements no longer cite cand-9032.")

    _, manifest, _ = read_csv(MANIFEST)
    if any(row["type"] == "archive" and "Tombeaux des Princes" in (row.get("canonical_name", "") + " " + row.get("name_en", "")) for row in manifest):
        raise SystemExit("A same-title archive KU now exists; compare it before keeping this as new.")

    prior_note = index_decision["resolution_note"]
    updated_alignment = [dict(row) for row in alignment]
    updated_by_id = {row["candidate_id"]: row for row in updated_alignment if not row["external_source"]}
    updated_by_id["cand-1474"].update(
        decision="new",
        process_ref=PROCESS_REF,
        resolution_note=(
            f"source_ref=index_entry=M.csv#11;pages=289n,290,291; body_candidate=cand-9032; "
            f"identity_peers=cand-9032; group={GROUP}; "
            "body_mentions=m-chp10-p291-published-volume-title,m-chp10-p289-note2-tombeaux; "
            "statements=st-chp10-p289-note2-1741-publication,st-chp10-p291-volume-publication-and-disappointment,st-chp10-p291-volume-plate-and-tomb-count. "
            "Index subentry Tombeaux des Princes identifies the same 1741 printed volume named in the chapter body; the title, edition year, and overlapping page anchors resolve this index-only candidate to cand-9032. "
            "Keep it in the same pending new archive group, not a separate publication. Distinct from cand-9030 (issued subscription pamphlet), cand-9031 (unrealized fifty-plate proposal), and the painting-series work. "
            "Haskell reports eighteen plates and nine allegorical tombs for the 1741 volume; this decision aligns bibliographic identity only and does not independently verify all reported contents or claims. "
            f"prior_resolution_note={prior_note}"
        ),
    )

    result_text = RESULT.read_text(encoding="utf-8-sig")
    replacements = [
        ("new=5,006（4,831个身份组）", "new=5,007（4,831个身份组）"),
        ("undecided=5,524。S4 已登记281组、映射352条成员候选；尚待登记4,550组、4,654条映射。", "undecided=5,523。S4 已登记281组、映射352条成员候选；尚待登记4,550组、4,655条映射。"),
        ("| new | 5,006 | 按 4,831 个当前身份组进入 S4；每组登记一个 KU |", "| new | 5,007 | 按 4,831 个当前身份组进入 S4；每组登记一个 KU |"),
        ("| undecided | 5,524 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |", "| undecided | 5,523 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |"),
        ("| archive | 78→61 | 1,247／1,215 | 29／1,186；1,212 | 0 | 18 | 757 |", "| archive | 78→61 | 1,248／1,215 | 29／1,186；1,213 | 0 | 18 | 756 |"),
        ("| **合计** | **1,767→1,026** | **5,006／4,831** | **281／4,550；4,654** | **8** | **99** | **5,524** |", "| **合计** | **1,767→1,026** | **5,007／4,831** | **281／4,550；4,655** | **8** | **99** | **5,523** |"),
    ]
    for old, new in replacements:
        if result_text.count(old) != 1:
            raise SystemExit(f"Expected one result occurrence of {old!r}, found {result_text.count(old)}")
        result_text = result_text.replace(old, new, 1)
    section = (
        "### S3 archive：McSwiny《Tombeaux des Princes》索引候选并组（2026-10-16）\n\n"
        "- `cand-1474`（M.csv#11，289n、290、291）由 `undecided` 改为 `new`，与正文候选 `cand-9032` 同属 `archive-group-25725e686a64`，待 S4 映射为一个 KU。索引短题名与正文中完整法文题名、1741 年出版信息及重叠页码相合；正文 mentions 与 statements 提供可回溯锚点。因该组已有 `new` 决定，本索引候选继续标 `new`，不另建第二个出版物组。\n"
        "- 边界：与已发行征订小册子 `cand-9030`、未实现的五十幅铜版计划卷 `cand-9031`、以及寓意墓葬画系列作品分开。Haskell 报告 1741 年卷有18幅、其中9幅为寓意墓葬；本轮只裁决文献身份，不独立核实全部内容或书内 claims。未添加外部身份行、KU、卡片或关系。"
    )
    marker = "### S4 按类型登记进度"
    if result_text.count(marker) != 1:
        raise SystemExit("Could not find the S4 type-progress insertion point.")
    result_text = result_text.replace(marker, section + "\n\n" + marker, 1)

    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    knowledge_text += (
        "\n\n### S3 archive：McSwiny《Tombeaux des Princes》索引候选并组（2026-10-16）\n\n"
        "- `cand-1474`（M.csv#11，索引子项 `Tombeaux des Princes`，289n、290、291）从 `undecided` 改为 `new`，加入 `archive-group-25725e686a64`；该组已有正文候选 `cand-9032`，整体待 S4 登记一个 archive KU。索引只提供定位，决定依据是该索引候选的题名及页码与正文候选的同书身份锚点吻合：完整法文题名、1741 年出版信息、具体卷册描述及重叠页码。直接证据为 mentions `m-chp10-p291-published-volume-title`、`m-chp10-p289-note2-tombeaux`，以及 statements `st-chp10-p289-note2-1741-publication`、`st-chp10-p291-volume-publication-and-disappointment`、`st-chp10-p291-volume-plate-and-tomb-count`。\n"
        "- 边界：`cand-9030` 是已发行、用于征订计划卷的小册子；`cand-9031` 是该小册子所述未实现的50幅铜版出版计划；`cand-9032` 是正文称1741年出版的实际卷册。1741卷与寓意墓葬画系列作品亦分别属于 archive 与 work。新增索引候选与正文候选同组，但仍按规则保留 `new` 决定，等待一个 KU 映射；未新增外部身份记录、KU、卡片或关系。\n"
        "- 原 `undecided` 理由称缺少该候选自己的正文 mention；本轮利用正文候选及索引重叠页码解除身份定位缺口。仍不把 Haskell 对版数、内容、出版经过或关系的陈述视为独立外部核实。"
    )

    updates = {
        ALIGNMENT: encode_csv(alignment_headers, updated_alignment, alignment_bom),
        RESULT: ("\ufeff" + result_text).encode("utf-8"),
        KNOWLEDGE: ("\ufeff" + knowledge_text).encode("utf-8"),
    }
    print("PREVIEW" if not args.apply else "APPLY")
    for path, content in updates.items():
        print(f"  {path.relative_to(ROOT)}: {sha256(path.read_bytes())} -> {sha256(content)}")
    print("  S3 candidate decisions:", dict(Counter(row["decision"] for row in primary)), "->", dict(Counter(row["decision"] for row in updated_alignment if not row["external_source"])))
    print(f"  identity group: cand-1474 + cand-9032 -> {GROUP}; S4 group count unchanged, pending member mappings +1")
    if not args.apply:
        print("Dry-run only; pass --apply to write the changes.")
        return

    for path in updates:
        backup = path.with_name(path.name + ".bak-s3-mcswiny-tombeaux-20261016")
        if backup.exists():
            raise SystemExit(f"Recovery copy already exists: {backup}")
        shutil.copy2(path, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s3-mcswiny-tombeaux-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied the archive identity decision and retained recovery copies.")


if __name__ == "__main__":
    main()
