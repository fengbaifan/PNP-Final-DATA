from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
from collections import defaultdict
from pathlib import Path

import yaml


ROOT = Path.cwd()
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
MANIFEST = TABLES / "ku-manifest.csv"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
KNOWLEDGE = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
SOURCE_16_PATH = "02-sources/02-Markdown/16_CHP-16_intro.md"
SOURCE_17_PATH = "02-sources/02-Markdown/17_CHP-17_sec_ii.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md"
BACKUP_SUFFIX = ".bak-s4-sasso-sale-20261016"

KU_ID = "units/events/sasso-personal-collection-auction-1803"
CARD_PATH = "04-knowledge/units/events/sasso-personal-collection-auction-1803.md"
GROUP = "sg3-event-cand-10715"
CANDIDATES = ["cand-10715", "cand-11549"]
QUOTE_16 = (
    "In the collection he made for himself which was auctioned after his death in 1803 "
    "there were a number of such pictures—by Giambattista and Gian Domenico Tiepolo, "
    "as well as one of his own copies of one of them, and 100 drawings"
)
QUOTE_17 = (
    "For instance, he almost certainly bought Zocchi’s double portrait of A. M. Zanetti "
    "and the Marchese\nGerini at the Sasso sale in 1803—sec Haskell, Bollettino dei Musei "
    "Civici Veneziani, i960, 3/4, pp. 32-7."
)


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bool]:
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader), has_bom


def encode_csv(fields: list[str], rows: list[dict[str, str]], has_bom: bool) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    text = stream.getvalue()
    return ("\ufeff" + text if has_bom else text).encode("utf-8")


def text_bytes(path: Path, text: str) -> bytes:
    has_bom = path.read_bytes().startswith(b"\xef\xbb\xbf")
    return ("\ufeff" + text if has_bom else text).encode("utf-8")


def group_of(note: str) -> str:
    match = re.search(r"group=([^;|\s]+)", note)
    return match.group(1) if match else ""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected one result occurrence of {old!r}, found {count}")
    return text.replace(old, new, 1)


def make_card() -> str:
    frontmatter = {
        "title": "萨索个人收藏拍卖（1803）（Auction of Giovanni Maria Sasso's Private Collection (1803)）",
        "name_en": "Auction of Giovanni Maria Sasso's Private Collection (1803)",
        "type": "event",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": BOOK_CITATION,
                "location": "第16章；印刷页374；OCR L22",
                "sentence_summary": "萨索为自己汇集的收藏在其去世后于1803年拍卖；本段列举了其中若干提埃波罗作品和素描。",
                "original_quotes": [{"source_span": "lines 22", "text": QUOTE_16}],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": SOURCE_16_PATH,
                    "source_span": "lines 22; print p. 374",
                },
            },
            {
                "citation": BOOK_CITATION,
                "location": "第17章；印刷页382；OCR L16–17；注4；被引文章未独立查阅",
                "sentence_summary": "Haskell称 Correr 几乎可以肯定在1803年 Sasso 拍卖中购入 Zocchi 的 Zanetti 与 Gerini 双人肖像，并转引一篇1960年文章。",
                "original_quotes": [{"source_span": "lines 16–17", "text": QUOTE_17}],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": SOURCE_17_PATH,
                    "source_span": "lines 16–17; print p. 382; footnote 4",
                },
            },
        ],
        "created": "2026-10-16",
        "updated": "2026-10-16",
        "process_ref": PROCESS_REF,
    }
    header = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    body = f"""## 内容

### 描述

**中文：** 本卡指向同一场1803年萨索个人收藏拍卖。Haskell第16章称，萨索为自己汇集的收藏在其去世后于1803年拍卖，并列举了提埃波罗作品、萨索本人临摹其中一件及100幅素描。第17章注4又称 Correr 几乎可以肯定在该场拍卖中购得佐基创作、描绘老扎内蒂与杰里尼侯爵的双人肖像。此处只记录 Haskell 的叙述；其所引拍卖目录及1960年期刊文章本轮未独立查阅，“几乎可以肯定”保留为来源判断。

**English:** This unit identifies the 1803 auction of Giovanni Maria Sasso's personal collection. Chapter 16 says the collection he assembled for himself was auctioned after his death in 1803, and notes works by the Tiepolos, one of Sasso's own copies of a Tiepolo work, and 100 drawings. In footnote 4 on p.382, Haskell says Correr almost certainly bought at that sale Zocchi's double portrait of A. M. Zanetti and the Marchese Gerini. This follows Haskell's account; the cited sale catalogue and 1960 journal article were not independently consulted, and “almost certainly” remains attributed to Haskell.

### 事件信息

| 项目 | 内容 | 证据 |
|---|---|---|
| 事件性质 | Sasso 为自己汇集的个人收藏拍卖 | S1；[第16章 p.374](../../../02-sources/02-Markdown/16_CHP-16_intro.md)（L22） |
| 时间 | 1803年；发生在 Sasso 去世后；原文未提供日月 | S1、S2；[第16章 p.374](../../../02-sources/02-Markdown/16_CHP-16_intro.md)（L22）；[第17章 p.382 注4](../../../02-sources/02-Markdown/17_CHP-17_sec_ii.md)（L16–17） |
| 原收藏者 | [乔万尼·马里亚·萨索（Giovanni Maria Sasso）](../persons/g-m-sasso.md)；此处指其为自己收集的藏品 | S1；[第16章 p.374](../../../02-sources/02-Markdown/16_CHP-16_intro.md)（L22） |
| 收藏内容举例 | Giambattista 与 Gian Domenico Tiepolo 的作品、萨索本人临摹其中一件及100幅素描；不是完整目录 | S1；[第16章 p.374](../../../02-sources/02-Markdown/16_CHP-16_intro.md)（L22） |
| 注4提及的作品与买家 | [老扎内蒂与杰里尼侯爵双人肖像](../works/giuseppe-zocchi-a-m-zanetti-the-elder-with-marchese-gerini.md)；Haskell称[泰奥多罗·科雷尔（Teodoro Correr）](../persons/teodoro-correr.md)几乎可以肯定在该场拍卖购得；这是来源的概率判断 | S2；[第17章 p.382 注4](../../../02-sources/02-Markdown/17_CHP-17_sec_ii.md)（L16–17） |

## 关系与证据

### 关系记录

尚无正式关系记录。作品购入及拍卖参与者关系留待 S6 审查；卡内保留 Haskell 的“几乎可以肯定”措辞，不改写为已核实交易事实。
"""
    return f"---\n{header}---\n\n{body.strip()}\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Register the Sasso 1803 cross-chapter event group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not (ROOT / "04-knowledge" / "accepted.yml").exists():
        raise SystemExit("Run this script from the project root.")

    source16 = (ROOT / SOURCE_16_PATH).read_text(encoding="utf-8-sig")
    source17 = (ROOT / SOURCE_17_PATH).read_text(encoding="utf-8-sig")
    if QUOTE_16 not in source16 or QUOTE_17 not in source17:
        raise SystemExit("A quoted passage does not match the chapter source files.")

    alignment_fields, alignments, alignment_bom = read_csv(ALIGNMENT)
    manifest_fields, manifest_rows, manifest_bom = read_csv(MANIFEST)
    candidate_rows = list(csv.DictReader((TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline="")))
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in CANDIDATES:
        if cid not in candidate_by_id or cid not in alignment_by_id:
            raise SystemExit(f"Missing S3 candidate or alignment row: {cid}")
        if candidate_by_id[cid].get("suggested_type") != "event":
            raise SystemExit(f"Unexpected type for {cid}: {candidate_by_id[cid].get('suggested_type')}")
        row = alignment_by_id[cid]
        if row.get("decision") != "new" or row.get("ku_id"):
            raise SystemExit(f"{cid} is no longer an unmapped new candidate.")
        if group_of(row.get("resolution_note", "")) != GROUP:
            raise SystemExit(f"{cid} is no longer assigned to {GROUP}.")
    members = sorted(
        row["candidate_id"] for row in alignments
        if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
        and group_of(row.get("resolution_note", "")) == GROUP
    )
    if members != sorted(CANDIDATES):
        raise SystemExit(f"Unexpected S3 membership for {GROUP}: {members}")
    if len(manifest_rows) != 1305 or any(row.get("ku_id") == KU_ID for row in manifest_rows):
        raise SystemExit("Unexpected manifest baseline or the S4 target already exists.")
    card_path = ROOT / CARD_PATH
    if card_path.exists():
        raise SystemExit(f"S4 card already exists: {CARD_PATH}")

    before = 286, 358, 4554, 4663
    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in CANDIDATES:
        planned_by_id[cid]["ku_id"] = KU_ID
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest_rows)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "event",
        "canonical_name": "萨索个人收藏拍卖（1803）",
        "name_en": "Auction of Giovanni Maria Sasso's Private Collection (1803)",
        "source_task": TASK,
        "card_path": CARD_PATH,
    })
    planned_manifest.sort(key=lambda row: row["ku_id"])

    accepted_text = ACCEPTED.read_text(encoding="utf-8-sig")
    accepted_lines = accepted_text.splitlines()
    if any(line == f"- {CARD_PATH}" for line in accepted_lines):
        raise SystemExit("Accepted path already exists.")
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_PATH),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_PATH}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    result_text = RESULT.read_text(encoding="utf-8-sig")
    result_text = replace_once(result_text, "S4 已登记286组、映射358条成员候选；尚待登记4,554组、4,663条映射。",
                               "S4 已登记287组、映射360条成员候选；尚待登记4,553组、4,661条映射。")
    result_text = replace_once(result_text, "1,305 KU；新组登记与待登记分类型统计见下表",
                               "1,306 KU；新组登记与待登记分类型统计见下表")
    result_text = replace_once(result_text, "| event | 7→7 | 235／231 | 14／217；220 | 0 | 0 | 115 |",
                               "| event | 7→7 | 235／231 | 15／216；218 | 0 | 0 | 115 |")
    follow_up = (
        "### S4 event follow-up：跨章 Sasso 1803 年拍卖组（2026-10-16）\n\n"
        "- `cand-10715`（第17章 p.382 注4）与 `cand-11549`（第16章 p.374）映射到同一事件组 `sg3-event-cand-10715`，登记为 `units/events/sasso-personal-collection-auction-1803`；候选和组内两个 source_ref 均保留在 alignment。\n"
        "- 第16章称 Sasso 为自己汇集的收藏在其去世后于1803年拍卖；第17章注4称 Correr 几乎可以肯定在该场拍卖购得 Zocchi 的 Zanetti—Gerini 双人肖像。卡片链接既有 Sasso、Teodoro Correr 与 work KU，不新增正式关系。原书引用的拍卖目录及1960年期刊文章未独立查阅，买入判断继续标为 Haskell 的“几乎可以肯定”。\n"
        "- 新增1张 event 卡、1条 manifest 映射、2条候选映射；累计S4登记287组/360条映射，待登记4,553组/4,661条映射；event 为15组已登记、216组/218条成员待登记。\n\n"
    )
    result_text = replace_once(result_text, "## 未解决项与交接限制", follow_up + "## 未解决项与交接限制")

    process_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    process_section = (
        "\n\n### S4 event follow-up：跨章 Sasso 1803 年拍卖组（2026-10-16）\n\n"
        "- S3 既有组 `sg3-event-cand-10715` 含 `cand-10715`（ch.17:17_CHP-17_sec_ii:L7–17）与后并入的 `cand-11549`（ch.16:16_CHP-16_intro:L16–22）；两项均为同一场1803年 Sasso 藏品拍卖。按该组登记1张 event KU `units/events/sasso-personal-collection-auction-1803`，两个成员候选均映射至该卡。\n"
        "- p.374 L22 支持 Sasso 为自己汇集的收藏在其去世后于1803年拍卖及藏品举例；p.382 L16–17 注4称 Correr 几乎可以肯定在该场拍卖购得 Zocchi 的 Zanetti 与 Marchese Gerini 双人肖像。后者精确链接至既有 `units/works/giuseppe-zocchi-a-m-zanetti-the-elder-with-marchese-gerini`，人物入口链接至既有 Sasso、Teodoro Correr KU；未把 S3 尚待身份裁决的 Gerini 人物候选强行合并。\n"
        "- Haskell 分别引述第16章的藏品叙述与第17章注4的购买判断；注4所引 sale catalogue 与 1960 年 *Bollettino dei Musei Civici Veneziani* 文章未独立查阅。卡片保留“几乎可以肯定”，不宣称已核实交易，不新增 `relations.csv` 正式边；相关购入与参与者边留待 S6。\n"
        "- 新增1张 event 卡、`ku-manifest.csv` 1条、alignment 2条成员映射及 `accepted.yml` 1条路径；字段行随后通过 `build_field_facts.py` 预检与 apply 登记。S4 累计287组/360条映射，待登记4,553组/4,661条映射；event 为15组已登记、216组/218条成员待登记；KU 总数1,306。\n"
    )
    if "### S4 event follow-up：跨章 Sasso 1803 年拍卖组" in process_text:
        raise SystemExit("S4 Sasso process section already exists.")
    process_text += process_section

    card_text = make_card()
    card_bytes = card_text.encode("utf-8-sig")
    frontmatter = yaml.safe_load(card_text.split("---\n", 2)[1])
    if frontmatter.get("type") != "event" or len(frontmatter.get("sources", [])) != 2:
        raise SystemExit("Generated card frontmatter failed validation.")

    updates = {
        ALIGNMENT: encode_csv(alignment_fields, planned_alignment, alignment_bom),
        MANIFEST: encode_csv(manifest_fields, planned_manifest, manifest_bom),
        ACCEPTED: text_bytes(ACCEPTED, planned_accepted),
        RESULT: text_bytes(RESULT, result_text),
        KNOWLEDGE: text_bytes(KNOWLEDGE, process_text),
        card_path: card_bytes,
    }
    print("DRY-RUN" if args.dry_run else "APPLY")
    for path, content in updates.items():
        old_hash = digest(path.read_bytes()) if path.exists() else "absent"
        print(f"  {path.relative_to(ROOT)}: {old_hash} -> {digest(content)}")
    print("  group=1; candidates=2; new cards=1; source quotes and cross-chapter group checked")
    print(f"  S4: {before[0]:,}/{before[1]:,} -> 287/360 groups/mappings; pending=4,553/4,661")
    print("  event: registered 14 -> 15 groups; manifest=1,305 -> 1,306")
    if args.dry_run:
        print("Dry-run passed; no files changed.")
        return

    backup_targets = [ALIGNMENT, MANIFEST, ACCEPTED, RESULT, KNOWLEDGE]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in backup_targets]
    if any(path.exists() for path in backups):
        raise SystemExit("A S4 Sasso recovery copy already exists; inspect before applying.")
    for original, backup in zip(backup_targets, backups, strict=True):
        shutil.copy2(original, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s4-sasso-sale-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied Sasso cross-chapter S4 event registration and retained recovery copies.")


if __name__ == "__main__":
    main()
