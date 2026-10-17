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

GROUP = "archive-group-25725e686a64"
MEMBERS = ("cand-1474", "cand-9032")
KU_ID = "units/archives/tombeaux-des-princes-mcswiny-1741"
CARD_REL = "04-knowledge/units/archives/tombeaux-des-princes-mcswiny-1741.md"
BACKUP_SUFFIX = ".bak-s4-mcswiny-tombeaux-des-princes-1741-20261016"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
BODY_FILE = "10_CHP-10_intro.md"
INDEX_FILE = "22_CHP-22Index_intro.md"
QUOTES = {
    "p291_title": (
        "The volume—Tombeaux des Princes grands capitaines et autres hommes illustres, "
        "qui ont fleuri dans la Grande-Bretagne vers la fin du XVII et le commencement "
        "du XVIII siecle— appeared in 1741, and was certainly very magnificent, but it "
        "must have disappointed McSwiny who had returned to England some ten years earlier."
    ),
    "p291_counts": (
        "There were eighteen instead of fifty plates, and only nine of the allegorical tombs "
        "were engraved—all from the Duke of Richmond’s collection."
    ),
    "p289_note": (
        "In 1741 McSwiny published nine of them in the Tombeaux des Princes and said that "
        "they all belonged to the Duke."
    ),
    "index": "Tombeaux des Princes, 289n, 290-91",
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
    title_zh = "《英国显要人物墓葬集》1741年刊本"
    title_en = (
        "Tombeaux des Princes grands capitaines et autres hommes illustres, qui ont fleuri "
        "dans la Grande-Bretagne vers la fin du XVII et le commencement du XVIII siècle (1741 edition)"
    )
    body_link = f"../../../02-sources/02-Markdown/{BODY_FILE}"
    index_link = f"../../../02-sources/02-Markdown/{INDEX_FILE}"
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第10章，印刷页291；Markdown行258-260；S2按页图确认题名末词为“siècle”",
            "sentence_summary": (
                "Haskell给出1741年卷册的完整法文题名，并称该卷有18幅版画，其中9幅寓意墓葬图被刻印；"
                "这些关于刊物内容的陈述未独立核验。"
            ),
            "original_quotes": [
                {"source_span": "lines 258-259", "text": QUOTES["p291_title"]},
                {"source_span": "line 259", "text": QUOTES["p291_counts"]},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{BODY_FILE}",
                "source_span": "lines 258-260; print p. 291; PDF physical p. 20",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第10章注2，印刷页289；Markdown行544；Haskell本人提示藏品归属存在混乱",
            "sentence_summary": (
                "Haskell称McSwiny于1741年在该卷册中刊出九幅方案图，并转述书中称它们均属Richmond公爵；"
                "同一注释提醒相关购藏经过混乱。"
            ),
            "original_quotes": [{"source_span": "line 544", "text": QUOTES["p289_note"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{BODY_FILE}",
                "source_span": "line 544; print p. 289, note 2",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "书末索引；Markdown行1853；索引短题名列289n、290-291",
            "sentence_summary": (
                "索引在McSwiny名下以短题名Tombeaux des Princes列出相关页码；与p.291正文完整题名、"
                "1741年刊行叙述及重叠页码对应。"
            ),
            "original_quotes": [{"source_span": "line 1853", "text": QUOTES["index"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{INDEX_FILE}",
                "source_span": "line 1853; index locators pp. 289-291",
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
    body = f"""## 内容

### 描述

**中文：** 本卡登记哈斯克尔第10章所述、1741年出版的 *Tombeaux des Princes grands capitaines et autres hommes illustres, qui ont fleuri dans la Grande-Bretagne vers la fin du XVII et le commencement du XVIII siècle*。第291页给出完整题名，称该卷有18幅版画，其中9幅寓意墓葬图被刻印；第289页注2称McSwiny在书中刊出九幅方案图，并转述其均属Richmond公爵，同时明确提醒实际购藏经过存在混乱。因此，版画数和归属均作为Haskell的书内报告保留，未独立核验。索引短题名及页码与正文身份锚点相合。身份入口： [Owen McSwiny](../persons/owen-mcswiny.md)。征订小册子和拟议的50幅版画卷册分别留在其S3对象边界内；本卡只表示1741年实际出版卷册。原刊未独立查阅。[第10章 p.291]({body_link})（L258–260）[第10章 p.289 注2]({body_link})（L544）[书末索引]({index_link})（L1853）

**English:** This card records the volume Haskell says appeared in 1741 under the title *Tombeaux des Princes grands capitaines et autres hommes illustres, qui ont fleuri dans la Grande-Bretagne vers la fin du XVII et le commencement du XVIII siècle*. On p. 291 he reports eighteen plates, including nine engraved allegorical tombs. Note 2 on p. 289 says McSwiny published nine scheme pictures in the volume and repeats its claim that they all belonged to the Duke of Richmond, while warning that the acquisition history is confused. The plate count and ownership remain Haskell’s reports and were not independently verified. The index short title and page references match the body identity anchors. Identity entry: [Owen McSwiny](../persons/owen-mcswiny.md). The subscription pamphlet and its proposed fifty-plate volume remain separate S3 objects; this card covers only the actual 1741 publication. The printed volume was not independently consulted. [Chapter 10, p. 291]({body_link}) (L258–260) [Chapter 10, p. 289, n. 2]({body_link}) (L544) [book index]({index_link}) (L1853)

### 文献身份与书内记载

| 字段 | 内容 | 证据 |
|---|---|---|
| 完整题名 | *Tombeaux des Princes grands capitaines et autres hommes illustres, qui ont fleuri dans la Grande-Bretagne vers la fin du XVII et le commencement du XVIII siècle*；S2按页图确认末词重音，Markdown OCR未保留 | [第10章 p.291]({body_link})（L258–259）；[书末索引]({index_link})（L1853） |
| 出版年份 | 1741；出版地、具体印刷者及版次未载 | [第10章 p.291]({body_link})（L258–259） |
| 版画数量 | Haskell报告全卷18幅版画，其中9幅寓意墓葬图被刻印；不将计划中的50幅视作实际数量 | [第10章 p.291]({body_link})（L259–260） |

### 身份边界

S3组 `{GROUP}` 包含索引候选 `cand-1474` 与正文／注释候选 `cand-9032`。索引短题名 *Tombeaux des Princes* 指向p.289注、p.290–291；第291页给出完整题名和1741年出版信息。该卷与征订小册子 `cand-9030`、未独立出版为一个50幅卷册的计划规格 `cand-9031` 及寓意墓葬画作系列分开；本卡不把卷册记载转为对各画作的所有权或制作关系。

## 关系与证据

当前没有登记正式关系。出版者、书内归属主张、插图和版画制作等S2关系候选留待S6逐条审查；本卡只登记出版物身份，来源陈述不等于正式关系。
"""
    return f"---\n{header}---\n\n{body}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Register McSwiny's 1741 Tombeaux des Princes volume in S4.")
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
    if len(manifest_rows) != 1317 or any(row.get("ku_id") == KU_ID for row in manifest_rows):
        raise SystemExit("Unexpected S4 baseline or target already registered.")
    for cid in MEMBERS:
        if cid not in candidate_by_id or cid not in alignment_by_id:
            raise SystemExit(f"Missing S3 candidate or alignment: {cid}")
        if candidate_by_id[cid].get("suggested_type") != "archive":
            raise SystemExit(f"Unexpected type for {cid}.")
        row = alignment_by_id[cid]
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

    body_source = collapse((ROOT / "02-sources" / "02-Markdown" / BODY_FILE).read_text(encoding="utf-8-sig"))
    index_source = collapse((ROOT / "02-sources" / "02-Markdown" / INDEX_FILE).read_text(encoding="utf-8-sig"))
    for quote in (QUOTES["p291_title"], QUOTES["p291_counts"], QUOTES["p289_note"]):
        if collapse(quote) not in body_source:
            raise SystemExit(f"Body source quote mismatch: {quote}")
    if QUOTES["index"] not in index_source:
        raise SystemExit("Book index quote mismatch.")
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
        "canonical_name": "《英国显要人物墓葬集》1741年刊本",
        "name_en": "Tombeaux des Princes grands capitaines et autres hommes illustres (1741 edition)",
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
        "S4 已登记298组、映射385条成员候选；尚待登记4,541组、4,636条映射。",
        "S4 已登记299组、映射387条成员候选；尚待登记4,540组、4,634条映射。")
    result_text = replace_once(result_text, "1,317 KU；新组登记与待登记分类型统计见下表",
                               "1,318 KU；新组登记与待登记分类型统计见下表")
    result_text = replace_once(result_text,
        "| archive | 79→61 | 1,258／1,220 | 38／1,182；1,202 | 0 | 18 | 745 |",
        "| archive | 79→61 | 1,258／1,220 | 39／1,181；1,200 | 0 | 18 | 745 |")
    result_text = replace_once(result_text,
        "| **合计** | **1,774→1,026** | **5,021／4,839** | **298／4,541；4,636** | **8** | **100** | **5,501** |",
        "| **合计** | **1,774→1,026** | **5,021／4,839** | **299／4,540；4,634** | **8** | **100** | **5,501** |")
    detail = (
        "### S4 archive：McSwiny《Tombeaux des Princes》1741年出版卷册（2026-10-16）\n\n"
        "- `cand-1474`（M.csv#11，索引短题名及289n、290–291页码）与正文候选 `cand-9032` 同属 `archive-group-25725e686a64`，映射至 `units/archives/tombeaux-des-princes-mcswiny-1741`。第10章p.291提供完整法文题名及1741年出版信息；S2按页图确认末词“siècle”，索引和正文OCR的题名形式及页码互相对应。\n"
        "- Haskell报告卷册有18幅版画，其中9幅寓意墓葬图被刻印；p.289注2同时报告九幅作品的归属主张，并提醒相关购藏经过混乱。以上均保留为书内报告，原刊及归属未独立核验。小册子 `cand-9030` 和未完成50幅规格的计划 `cand-9031` 保持分开；本卡不升级为画作制作或所有权正式边。\n"
        "- 新增1张archive卡、1条manifest映射、2条候选映射和1条accepted路径。S4累计登记299组/387条映射，待登记4,540组/4,634条映射；archive为39组已登记、1,181组/1,200条成员待登记；KU总数1,318。\n\n"
    )
    result_text = replace_once(result_text, "## 未解决项与交接限制", detail + "## 未解决项与交接限制")

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    if "### S4 archive：McSwiny《Tombeaux des Princes》1741年出版卷册" in process_text:
        raise SystemExit("McSwiny 1741 volume S4 process record already exists.")
    process_text += (
        "\n\n### S4 archive：McSwiny《Tombeaux des Princes》1741年出版卷册（2026-10-16）\n\n"
        "- 按S3组 `archive-group-25725e686a64` 登记 `cand-1474` 与 `cand-9032`。索引短题名 `Tombeaux des Princes` 指向p.289注、p.290–291；第291页正文给出完整法文题名、1741年刊行说明及卷册版数，足以将索引候选映射到正文同一刊物。S2页图已校读末词为 `siècle`，Markdown OCR不含重音。\n"
        "- Haskell报告18幅版画、其中9幅寓意墓葬图被刻印；p.289注2称McSwiny刊出了九幅方案图并转述归属Richmond公爵的说法，同时提醒购藏史混乱。未独立查阅原刊或核验归属。征订小册子 `cand-9030`、未实现为50幅出版规格的计划候选 `cand-9031`、墓葬画作系列均保留各自边界。\n"
        "- 新增 `units/archives/tombeaux-des-princes-mcswiny-1741`、manifest 1条、alignment 2条候选映射和accepted 1条路径；未新增正式关系。S4累计299组/387条映射，待登记4,540组/4,634条映射；archive为39组已登记、1,181组/1,200条成员待登记；KU总数1,318。字段行经 `build_field_facts.py` 预检与apply登记。\n"
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
    print(f"  group={GROUP}; candidates=2; title/year=Tombeaux des Princes / 1741")
    print("  S4=298/385 -> 299/387; pending=4,540/4,634; KU=1,318")
    print("  archive=38/1,182 -> 39/1,181 groups; pending candidates=1,200")
    if args.dry_run:
        print("Dry-run passed; no files changed.")
        return

    backup_targets = [ALIGNMENT, MANIFEST, ACCEPTED, PROCESS, RESULT]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in backup_targets]
    if any(path.exists() for path in backups):
        raise SystemExit("A McSwiny volume S4 recovery copy already exists; inspect before applying.")
    for original, backup in zip(backup_targets, backups, strict=True):
        shutil.copy2(original, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s4-mcswiny-tombeaux-des-princes-1741-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied McSwiny 1741 volume registration.")


if __name__ == "__main__":
    main()
