from __future__ import annotations

import argparse
import csv
import hashlib
import io
import re
import shutil
from pathlib import Path

import yaml


ROOT = Path.cwd()
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
MANIFEST = TABLES / "ku-manifest.csv"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md"
DATE = "2026-10-16"

GROUP = "archive-group-mcswiny-ladies-gentlemen-pamphlet"
MEMBERS = ("cand-1473", "cand-9030")
KU_ID = "units/archives/mcswiny-ladies-gentlemen-taste-pamphlet"
CARD_REL = "04-knowledge/units/archives/mcswiny-ladies-gentlemen-taste-pamphlet.md"
BACKUP_SUFFIX = ".bak-s4-mcswiny-ladies-gentlemen-pamphlet-20261016"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
SOURCE_FILE = "10_CHP-10_intro.md"
QUOTES = {
    "p290": "Some time in the 1730s he issued a pamphlet addressed ‘To the Ladies and Gentlemen of Taste’ in which he invited subscriptions for a magnificent volume",
    "p288n1": "In the pamphlet To the Ladies and Gentlemen of Taste (no date), of which there is a copy in the British Museum.",
    "p291": "There were eighteen instead of fifty plates, and only nine of the allegorical tombs were engraved",
}


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


def encode_text(path: Path, text: str) -> bytes:
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
        raise SystemExit(f"Expected one occurrence of {old!r}, found {count}")
    return text.replace(old, new, 1)


def collapse(text: str) -> str:
    return " ".join(text.split())


def make_card() -> str:
    title_zh = "致品味女士与先生的征订小册子（约1730年代）"
    title_en = "Subscription Pamphlet Addressed ‘To the Ladies and Gentlemen of Taste’ (c. 1730s)"
    source_path = f"../../../02-sources/02-Markdown/{SOURCE_FILE}"
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第10章，印刷页290；Markdown行247-248；刊行时间为约数，所征订卷册为计划项目",
            "sentence_summary": (
                "Haskell称McSwiny在1730年代某时发行一份面向“To the Ladies and Gentlemen of Taste”的小册子，"
                "邀请读者为一部计划中的大型卷册订阅。"
            ),
            "original_quotes": [{"source_span": "lines 247-248", "text": QUOTES["p290"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{SOURCE_FILE}",
                "source_span": "lines 247-248; print p. 290",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第10章注1，印刷页288；Markdown行540；原注称小册子无日期，并报告当时大英博物馆藏有一份",
            "sentence_summary": (
                "Haskell在第288页注1称该小册子没有日期，并报告他写作时大英博物馆藏有一份；"
                "这不是对当前馆藏状态的核验。"
            ),
            "original_quotes": [{"source_span": "line 540", "text": QUOTES["p288n1"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{SOURCE_FILE}",
                "source_span": "line 540; print p. 288, note 1",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第10章，印刷页291；Markdown行259-260；对照实际1741年卷册的版数",
            "sentence_summary": (
                "Haskell称1741年实际出版的Tombeaux des Princes有18幅版画，而小册子所述计划为50幅；"
                "计划规格不证明50幅版本曾实际刊行。"
            ),
            "original_quotes": [{"source_span": "lines 259-260", "text": QUOTES["p291"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{SOURCE_FILE}",
                "source_span": "lines 259-260; print p. 291",
            },
        },
    ]
    frontmatter = {
        "title": f"{title_zh}（{title_en}）",
        "name_en": title_en,
        "type": "archive",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": PROCESS_REF,
    }
    header = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source_link = f"[{SOURCE_FILE}]({source_path})"
    person_link = "[Owen McSwiny](../persons/owen-mcswiny.md)"
    body = f"""## 内容

### 描述

**中文：** 本卡记录哈斯克尔所述、面向“To the Ladies and Gentlemen of Taste”而写的征订小册子。第10章称Owen McSwiny在1730年代某时发行此册，并邀请读者为一部计划中的大型卷册订阅；同章p.288注1称该小册子无日期，并报告哈斯克尔写作时大英博物馆藏有一份。前者是约略刊行时期，后者是注释对册上日期的说明，两者均按原文范围保留；没有核验当前馆藏。小册子与计划卷册是不同对象；哈斯克尔称1741年实际出版的 *Tombeaux des Princes* 只有18幅版画，而非征订说明中的50幅，本卡不把计划规格当作已出版版本。刊行者身份入口：{person_link}。小册子与被引版本均未独立查阅。{source_link}（L247–248、L259–260、L540）

**English:** This card records the subscription pamphlet addressed “To the Ladies and Gentlemen of Taste” in Haskell’s account. Chapter 10 says Owen McSwiny issued it sometime in the 1730s and invited subscriptions for a proposed large volume; note 1 on p. 288 calls the pamphlet undated and reports a copy at the British Museum at Haskell’s source time. The approximate issue period and the note’s statement about the pamphlet’s date are kept within their source scope; present-day holdings were not checked. The pamphlet and proposed volume are distinct objects. Haskell says the actual *Tombeaux des Princes* published in 1741 had eighteen plates, not the fifty in the subscription proposal; this card does not treat the proposal as a completed edition. Publisher identity entry: {person_link}. Neither the pamphlet nor the cited edition was independently consulted. {source_link} (L247–248, L259–260, L540)

### 文献身份与书内记载

| 字段 | 内容 | 证据 |
|---|---|---|
| 称呼／题名形式 | “To the Ladies and Gentlemen of Taste”；哈斯克尔称小册子以此语称呼读者，未提供题名页 | {source_link}（L247–248、L540） |
| 刊行时间 | 哈斯克尔称在1730年代某时发行；第288页注1注明小册子“no date”，不据此推定具体年份 | {source_link}（L247、L540） |
| 用途 | 邀请读者为计划中的大型卷册订阅；不等于计划卷册已按50幅版画规格刊行 | {source_link}（L247–248、L259–260） |

### 身份边界

S3组 `{GROUP}` 包含索引候选 `cand-1473` 与正文／注释候选 `cand-9030`：正文及第288页注1反复使用同一称呼，索引子目指向该注释。小册子本身不与计划卷册候选 `cand-9031` 或1741年实际出版卷册候选 `cand-9032` 合并；后者的题名为 *Tombeaux des Princes grands capitaines et autres hommes illustres, qui ont fleuri dans la Grande-Bretagne vers la fin du XVII et le commencement du XVIII siecle*，其实际出版记录留在独立身份组。原件及当前馆藏未独立核验。

## 关系与证据

当前没有登记正式关系。`st-chp10-p288-n01-british-museum-copy` 所述馆藏关系仍待S6审查；McSwiny的刊行关系由书内来源支持，但本卡不将字段或身份链接直接写成正式关系。
"""
    return f"---\n{header}---\n\n{body}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Register McSwiny's subscription pamphlet identity group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignment_rows, alignment_bom = read_csv(ALIGNMENT)
    manifest_fields, manifest_rows, manifest_bom = read_csv(MANIFEST)
    _, candidates, _ = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row
        for row in alignment_rows
        if row.get("candidate_id") and not row.get("external_source")
    }
    if len(manifest_rows) != 1316 or any(row.get("ku_id") == KU_ID for row in manifest_rows):
        raise SystemExit("Unexpected S4 baseline or target already registered.")
    for cid in MEMBERS:
        if cid not in candidate_by_id or cid not in alignment_by_id:
            raise SystemExit(f"Missing S3 candidate or alignment: {cid}")
        candidate = candidate_by_id[cid]
        row = alignment_by_id[cid]
        if candidate.get("suggested_type") != "archive":
            raise SystemExit(f"Unexpected type for {cid}.")
        if row.get("decision") != "new" or row.get("ku_id") or group_of(row.get("resolution_note", "")) != GROUP:
            raise SystemExit(f"{cid} is no longer an unmapped member of {GROUP}.")
    group_members = {
        row["candidate_id"] for row in alignment_rows
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and group_of(row.get("resolution_note", "")) == GROUP
    }
    if group_members != set(MEMBERS):
        raise SystemExit(f"Unexpected S3 group membership: {sorted(group_members)}")
    card_path = ROOT / CARD_REL
    if card_path.exists():
        raise SystemExit(f"S4 card already exists: {CARD_REL}")

    source_text = collapse((ROOT / "02-sources" / "02-Markdown" / SOURCE_FILE).read_text(encoding="utf-8-sig"))
    for quote in QUOTES.values():
        if collapse(quote) not in source_text:
            raise SystemExit(f"Source quote mismatch: {quote}")
    if not (ROOT / "04-knowledge" / "units" / "persons" / "owen-mcswiny.md").exists():
        raise SystemExit("The linked Owen McSwiny identity card is missing.")

    planned_alignment = [dict(row) for row in alignment_rows]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in MEMBERS:
        planned_by_id[cid]["ku_id"] = KU_ID
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."

    planned_manifest = list(manifest_rows)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "archive",
        "canonical_name": "致品味女士与先生的征订小册子（约1730年代）",
        "name_en": "Subscription Pamphlet Addressed ‘To the Ladies and Gentlemen of Taste’ (c. 1730s)",
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    planned_manifest.sort(key=lambda row: row["ku_id"])

    accepted_text = ACCEPTED.read_text(encoding="utf-8-sig")
    accepted_lines = accepted_text.splitlines()
    if any(line.strip() == f"- {CARD_REL}" for line in accepted_lines):
        raise SystemExit("Accepted path already exists.")
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    result_text = RESULT.read_text(encoding="utf-8-sig")
    result_text = replace_once(result_text,
        "S4 已登记297组、映射383条成员候选；尚待登记4,542组、4,638条映射。",
        "S4 已登记298组、映射385条成员候选；尚待登记4,541组、4,636条映射。")
    result_text = replace_once(result_text, "1,316 KU；新组登记与待登记分类型统计见下表",
                               "1,317 KU；新组登记与待登记分类型统计见下表")
    result_text = replace_once(result_text,
        "| archive | 79→61 | 1,258／1,220 | 37／1,183；1,204 | 0 | 18 | 745 |",
        "| archive | 79→61 | 1,258／1,220 | 38／1,182；1,202 | 0 | 18 | 745 |")
    result_text = replace_once(result_text,
        "| **合计** | **1,774→1,026** | **5,021／4,839** | **297／4,542；4,638** | **8** | **100** | **5,501** |",
        "| **合计** | **1,774→1,026** | **5,021／4,839** | **298／4,541；4,636** | **8** | **100** | **5,501** |")
    detail = (
        "### S4 archive：McSwiny《To the Ladies and Gentlemen of Taste》征订小册子（2026-10-16）\n\n"
        "- `cand-1473`（M.csv#10，索引指向p.288n）与 `cand-9030`（第10章p.290正文、p.288注1）同属 `archive-group-mcswiny-ladies-gentlemen-pamphlet`，映射至 `units/archives/mcswiny-ladies-gentlemen-taste-pamphlet`。正文称McSwiny在1730年代某时发行小册子并征订计划卷册；注1称小册子无日期，并报告Haskell写作时大英博物馆藏本。当前馆藏未核验。\n"
        "- 计划中的50幅版画卷册（`cand-9031`）与1741年实际出版的 *Tombeaux des Princes*（`cand-9032`）均与小册子分开；Haskell记1741年卷有18幅版画。本卡不把征订计划规格当作已发行实体。相关出版者与馆藏正式关系留待S6。\n"
        "- 新增1张archive卡、1条manifest映射、2条候选映射和1条accepted路径。S4累计登记298组/385条映射，待登记4,541组/4,636条映射；archive为38组已登记、1,182组/1,202条成员待登记；KU总数1,317。\n\n"
    )
    result_text = replace_once(result_text, "## 未解决项与交接限制", detail + "## 未解决项与交接限制")

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    if "### S4 archive：McSwiny《To the Ladies and Gentlemen of Taste》征订小册子" in process_text:
        raise SystemExit("McSwiny pamphlet S4 process record already exists.")
    process_text += (
        "\n\n### S4 archive：McSwiny《To the Ladies and Gentlemen of Taste》征订小册子（2026-10-16）\n\n"
        "- 依现有S3组 `archive-group-mcswiny-ladies-gentlemen-pamphlet` 登记 `cand-1473` 与 `cand-9030`。索引子目指向第288页注1；第10章正文p.290与注1 p.288均识别同一小册子。正文给出“1730年代某时”的约略刊行时间，注释称小册子无日期；一条是刊行时间概述，一条是册上日期说明，不提升为精确年份。\n"
        "- 新KU `units/archives/mcswiny-ladies-gentlemen-taste-pamphlet` 记录邀请订阅的已发行小册子。Haskell所述计划卷册 `cand-9031` 与1741年实际出版物 `cand-9032` 均不并入；p.291报告实际卷为18幅而征订计划为50幅。British Museum藏本仅保留为Haskell写作时的报告，不视为当前馆藏核验。\n"
        "- 新增1张archive卡、manifest 1条、alignment 2条候选映射及accepted 1条路径。没有新增正式关系；出版社身份和来源时间馆藏陈述留待S6。字段行经 `build_field_facts.py` 预检与apply登记。S4累计298组/385条映射，待登记4,541组/4,636条映射；archive为38组已登记、1,182组/1,202条成员待登记；KU总数1,317。\n"
    )

    card_text = make_card()
    frontmatter = yaml.safe_load(card_text.split("---\n", 2)[1])
    if frontmatter.get("type") != "archive" or len(frontmatter.get("sources", [])) != 3:
        raise SystemExit("Generated card frontmatter failed validation.")
    updates = {
        ALIGNMENT: encode_csv(alignment_fields, planned_alignment, alignment_bom),
        MANIFEST: encode_csv(manifest_fields, planned_manifest, manifest_bom),
        ACCEPTED: encode_text(ACCEPTED, planned_accepted),
        PROCESS: encode_text(PROCESS, process_text),
        RESULT: encode_text(RESULT, result_text),
        card_path: card_text.encode("utf-8-sig"),
    }
    print("DRY-RUN" if args.dry_run else "APPLY")
    for path, content in updates.items():
        old_hash = digest(path.read_bytes()) if path.exists() else "absent"
        print(f"  {path.relative_to(ROOT)}: {old_hash} -> {digest(content)}")
    print(f"  group={GROUP}; candidates=2; source pages=288, 290, 291")
    print("  S4=297/383 -> 298/385; pending=4,541/4,636; KU=1,317")
    print("  archive=37/1,183 -> 38/1,182 groups; pending candidates=1,202")
    if args.dry_run:
        print("Dry-run passed; no files changed.")
        return

    backup_targets = [ALIGNMENT, MANIFEST, ACCEPTED, PROCESS, RESULT]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in backup_targets]
    if any(path.exists() for path in backups):
        raise SystemExit("A McSwiny S4 recovery copy already exists; inspect before applying.")
    for original, backup in zip(backup_targets, backups, strict=True):
        shutil.copy2(original, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s4-mcswiny-ladies-gentlemen-pamphlet-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied McSwiny subscription pamphlet registration.")


if __name__ == "__main__":
    main()
