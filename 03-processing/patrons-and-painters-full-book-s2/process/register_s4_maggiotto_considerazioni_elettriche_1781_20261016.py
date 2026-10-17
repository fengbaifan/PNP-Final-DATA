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
CANDIDATES = TABLES / "entity-candidates.csv"
SOURCES = TABLES / "sources.csv"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md"
DATE = "2026-10-16"

GROUP = "archive-group-maggiotto-considerazioni-elettriche-1781"
MEMBERS = ("cand-1490",)
KU_ID = "units/archives/considerazioni-elettriche-1781"
CARD_REL = "04-knowledge/units/archives/considerazioni-elettriche-1781.md"
BACKUP_SUFFIX = ".bak-s4-maggiotto-considerazioni-elettriche-1781-20261016"
BODY_FILE = "10_CHP-10_sec_ii.md"
INDEX_FILE = "22_CHP-22Index_intro.md"
TRECCANI_URL = (
    "https://www.treccani.it/enciclopedia/"
    "fedeli-francesco-detto-il-maggiotto_(Dizionario-Biografico)/"
)
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
BODY_QUOTE = (
    "Another artist at the end of the century, Francesco\n"
    "Maggiotto, was so far affected by advanced scientific ideas that he actually invented "
    "an electrical machine and wrote a treatise on the subject."
)
NOTE_QUOTE = (
    "1 See Andrea Tessier, 1882, pp. 289-315, and Considerazioni elettriche del signor "
    "Francesco Maggiotto— no date or publisher indicated—[Biblioteca Correr, Venice—Misc: 105113]."
)
INDEX_QUOTE = "Considerazioni elettriche, 325n"
TRECCANI_QUOTE = "Considerazioni elettriche, Venezia 1781"


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


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected one occurrence of {old!r}, found {count}")
    return text.replace(old, new, 1)


def collapse(text: str) -> str:
    return " ".join(text.split())


def group_of(note: str) -> str:
    match = re.search(r"group=([^;|\s]+)", note)
    return match.group(1) if match else ""


def make_card() -> str:
    title_zh = "《电学考论》"
    title_en = "Electrical Considerations (Considerazioni elettriche)"
    body_link = f"../../../02-sources/02-Markdown/{BODY_FILE}"
    index_link = f"../../../02-sources/02-Markdown/{INDEX_FILE}"
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第10章，印刷页325；Markdown行205–206；Haskell称Maggiotto写有电学机器论著",
            "sentence_summary": (
                "Haskell称Francesco Maggiotto写过一篇关于电学机器的论著；这是作者对人物及其著述的叙述，"
                "本轮未独立查阅原刊或核验机器相关陈述。"
            ),
            "original_quotes": [{"source_span": "lines 205–206", "text": BODY_QUOTE}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{BODY_FILE}",
                "source_span": "lines 205–206; print p. 325",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第10章注1，印刷页325；Markdown行329；Haskell报告其引用本的Correr定位及本上未标日期、出版者",
            "sentence_summary": (
                "Haskell注1以该题名和作者形式引用一份Biblioteca Correr本，定位为Misc. 105113，"
                "并称其未标日期或出版者；这是Haskell所记的来源时点定位，未据此确认当前馆藏。"
            ),
            "original_quotes": [{"source_span": "line 329", "text": NOTE_QUOTE}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{BODY_FILE}",
                "source_span": "line 329; print p. 325, note 1",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "书末索引；Markdown行1869；Maggiotto名下子目指向第325页注1",
            "sentence_summary": (
                "书末索引在Maggiotto名下列出Considerazioni elettriche及325页注释定位，"
                "与第10章注1题名相符。"
            ),
            "original_quotes": [{"source_span": "line 1869", "text": INDEX_QUOTE}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{INDEX_FILE}",
                "source_span": "line 1869; index locator p. 325, note",
            },
        },
        {
            "citation": (
                "Ettore Merkel, “Fedeli, Francesco, detto il Maggiotto,” "
                "Dizionario Biografico degli Italiani 45 (1995). "
                f"{TRECCANI_URL}. Accessed 2026-09-25."
            ),
            "url": TRECCANI_URL,
            "location": "有关物理兴趣及印刷小册子的段落（网页lines 53–54）",
            "accessed": DATE,
            "sentence_summary": (
                "Treccani DBI将Considerazioni elettriche列为Francesco Fedeli（detto il Maggiotto）"
                "名下、威尼斯1781年出版的印刷小册子之一；用于题名、作者及出版信息的书目身份对齐，"
                "不确认哈斯克尔所引Correr副本的馆藏状态。"
            ),
            "original_quotes": [
                {"source_span": "paragraph on printed booklets, line 54", "text": TRECCANI_QUOTE}
            ],
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

**中文：** 本卡登记意大利语题名 *Considerazioni elettriche*。中文题名“电学考论”为项目暂译，不声称是原刊所题。Treccani DBI将其列为Francesco Fedeli（别名Maggiotto）名下、威尼斯1781年出版的印刷小册子。Haskell第10章p.325称Francesco Maggiotto写有一篇关于电学机器的论著；该页注1引用同名题名，并报告一份[威尼斯Correr图书馆](../institutions/correr-library.md)本，定位为Misc. 105113，且称所据本未标日期或出版者。Treccani的书目记载支持题名、作者和出版地／年份，不核实Haskell所引具体副本或该馆当前保管状态；原刊及机器陈述本轮未独立查阅。作者身份入口：[Francesco Fedeli, detto il Maggiotto](../persons/francesco-maggiotto.md)。[第10章 p.325]({body_link})（L205–206、L329）[书末索引]({index_link})（L1869）

**English:** This card records the Italian title *Considerazioni elettriche*. The Chinese title “电学考论” is a project translation, not a claimed title of the original publication. Treccani’s DBI lists it among the printed booklets published under Francesco Fedeli, known as Maggiotto, in Venice in 1781. Chapter 10, p. 325, says that Francesco Maggiotto wrote a treatise on an electrical machine; note 1 cites the same title and reports a copy at the [Correr Library in Venice](../institutions/correr-library.md), shelfmark Misc. 105113, while stating that the cited copy has no date or publisher indicated. Treccani supports the bibliographic title, author, place, and year; it does not verify Haskell’s specific Correr copy or its present custody. The original publication and the machine-related account were not independently consulted. Identity entry: [Francesco Fedeli, detto il Maggiotto](../persons/francesco-maggiotto.md). [Chapter 10, p. 325]({body_link}) (L205–206, L329) [book index]({index_link}) (L1869)

### 文献身份与书内记载

| 字段 | 内容 | 证据 |
|---|---|---|
| 原题 | *Considerazioni elettriche*；“电学考论”为项目暂译 | S2；S3；S4 |
| 文献类型 | Treccani列为Francesco Fedeli（Maggiotto）名下的印刷小册子之一；Haskell称之为论著 | S1；S2；S4 |
| 作者 | Francesco Maggiotto；对应既有人物卡[Francesco Fedeli, detto il Maggiotto](../persons/francesco-maggiotto.md) | S1；S2；S4 |
| 出版信息 | 威尼斯，1781；据Treccani的书目条目。Haskell所引Correr本据称未标日期或出版者；本卡不推定出版者或具体版次 | S2；S4 |
| Haskell所引本的定位 | Haskell报告Biblioteca Correr, Venice, Misc. 105113；属来源时点的书内引注，当前馆藏状态未核 | S2 |

## 关系与证据

当前没有登记正式关系。作者信息按书内引注和外部书目来源呈现，并链接至既有人物卡；正式著作关系仍待关系阶段逐条审查。Correr馆藏号只作为Haskell所报告的定位，不表示已核实当前保管关系。
"""
    return f"---\n{header}---\n\n{body}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Register Maggiotto's 1781 Considerazioni elettriche in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignment_rows, alignment_bom = read_csv(ALIGNMENT)
    manifest_fields, manifest_rows, manifest_bom = read_csv(MANIFEST)
    _, candidates, _ = read_csv(CANDIDATES)
    _, source_rows, _ = read_csv(SOURCES)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    target_rows = [
        row for row in alignment_rows
        if row.get("candidate_id") == MEMBERS[0] and not row.get("external_source")
    ]
    if len(manifest_rows) != 1318 or any(row.get("ku_id") == KU_ID for row in manifest_rows):
        raise SystemExit("Unexpected S4 baseline or target already registered.")
    if len(target_rows) != 1 or MEMBERS[0] not in candidate_by_id:
        raise SystemExit("Expected one candidate decision row and one S3 candidate.")
    candidate = candidate_by_id[MEMBERS[0]]
    row = target_rows[0]
    if candidate.get("suggested_type") != "archive":
        raise SystemExit(f"Unexpected type for {MEMBERS[0]}.")
    if row.get("decision") != "new" or row.get("ku_id") or group_of(row.get("resolution_note", "")) != GROUP:
        raise SystemExit(f"{MEMBERS[0]} is no longer an unmapped member of {GROUP}.")
    group_members = {
        r["candidate_id"] for r in alignment_rows
        if r.get("candidate_id") and not r.get("external_source")
        and r.get("decision") == "new" and group_of(r.get("resolution_note", "")) == GROUP
    }
    if group_members != set(MEMBERS):
        raise SystemExit(f"Unexpected S3 group membership: {sorted(group_members)}")
    external_rows = [
        r for r in alignment_rows
        if r.get("candidate_id") == MEMBERS[0] and r.get("external_source")
        and r.get("external_id") == TRECCANI_URL and r.get("decision") == "new"
    ]
    if not external_rows:
        raise SystemExit("The S3 Treccani bibliography row is missing.")
    if not any(TRECCANI_URL in r.get("url", "") or TRECCANI_URL in r.get("source", "")
               or TRECCANI_URL in r.get("citation", "") for r in source_rows):
        source_file_text = SOURCES.read_text(encoding="utf-8-sig")
        if TRECCANI_URL not in source_file_text:
            raise SystemExit("Treccani source is not registered in sources.csv.")
    card_path = ROOT / CARD_REL
    if card_path.exists():
        raise SystemExit(f"S4 card already exists: {CARD_REL}")
    if not (ROOT / "04-knowledge" / "units" / "persons" / "francesco-maggiotto.md").exists():
        raise SystemExit("The linked Francesco Maggiotto person card is missing.")
    if not (ROOT / "04-knowledge" / "units" / "institutions" / "correr-library.md").exists():
        raise SystemExit("The linked Correr Library card is missing.")

    body_source = collapse((ROOT / "02-sources" / "02-Markdown" / BODY_FILE).read_text(encoding="utf-8-sig"))
    index_source = collapse((ROOT / "02-sources" / "02-Markdown" / INDEX_FILE).read_text(encoding="utf-8-sig"))
    if collapse(BODY_QUOTE) not in body_source or collapse(NOTE_QUOTE) not in body_source:
        raise SystemExit("The chapter body or note quote does not match the current source file.")
    if INDEX_QUOTE not in index_source:
        raise SystemExit("The index quote does not match the current source file.")

    planned_alignment = [dict(r) for r in alignment_rows]
    planned_target = next(r for r in planned_alignment
                          if r.get("candidate_id") == MEMBERS[0] and not r.get("external_source"))
    planned_target["ku_id"] = KU_ID
    planned_target["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."

    planned_manifest = list(manifest_rows)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "archive",
        "canonical_name": "《电学考论》",
        "name_en": "Electrical Considerations (Considerazioni elettriche)",
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    planned_manifest.sort(key=lambda r: r["ku_id"])

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
    result_text = replace_once(
        result_text,
        "S4 已登记299组、映射387条成员候选；尚待登记4,540组、4,634条映射。",
        "S4 已登记300组、映射388条成员候选；尚待登记4,539组、4,633条映射。",
    )
    result_text = replace_once(result_text, "1,318 KU；新组登记与待登记分类型统计见下表",
                               "1,319 KU；新组登记与待登记分类型统计见下表")
    result_text = replace_once(
        result_text,
        "| archive | 79→61 | 1,258／1,220 | 39／1,181；1,200 | 0 | 18 | 745 |",
        "| archive | 79→61 | 1,258／1,220 | 40／1,180；1,199 | 0 | 18 | 745 |",
    )
    result_text = replace_once(
        result_text,
        "| **合计** | **1,774→1,026** | **5,021／4,839** | **299／4,540；4,634** | **8** | **100** | **5,501** |",
        "| **合计** | **1,774→1,026** | **5,021／4,839** | **300／4,539；4,633** | **8** | **100** | **5,501** |",
    )
    detail = (
        "### S4 archive：Francesco Maggiotto《Considerazioni elettriche》1781年小册子（2026-10-16）\n\n"
        "- S3组 `archive-group-maggiotto-considerazioni-elettriche-1781` 仅含索引候选 `cand-1490`（M.csv#27，325n）。第10章p.325称Francesco Maggiotto写有关于电学机器的论著，注1列出同题名、Correr定位Misc. 105113，并称所引本没有日期或出版者信息；书末索引在Maggiotto名下列同题名及325n。\n"
        "- Treccani DBI（Ettore Merkel, vol.45, 1995）将 *Considerazioni elettriche* 列为Maggiotto名下、威尼斯1781年刊行的印刷小册子。该记录用于书目身份、作者、出版地和年份；不据此确认Haskell所引具体副本或当前馆藏，也不核实机器陈述。中文题名《电学考论》为项目暂译；出版者和版次未载。1882年Tessier文章 `cand-9779` 与本书分开，其他1781年电学小册子亦保持独立。\n"
        "- 新增 `units/archives/considerazioni-elettriche-1781`、1条manifest映射、1条候选映射和1条accepted路径；作者入口链接到既有人物卡，不登记正式著作关系，关系留待S6。字段行经 `build_field_facts.py` 预检与apply登记。S4累计300组/388条映射，待登记4,539组/4,633条映射；archive为40组已登记、1,180组/1,199条成员待登记；KU总数1,319。\n\n"
    )
    result_text = replace_once(result_text, "## 未解决项与交接限制", detail + "## 未解决项与交接限制")

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    heading = "### S4 archive：Francesco Maggiotto《Considerazioni elettriche》1781年小册子"
    if heading in process_text:
        raise SystemExit("Maggiotto S4 process record already exists.")
    process_text += (
        f"\n\n{heading}（2026-10-16）\n\n"
        "- S3组 `archive-group-maggiotto-considerazioni-elettriche-1781` 仅含 `cand-1490`（M.csv#27，索引子目 *Considerazioni elettriche*，p.325n）。第10章p.325以Francesco Maggiotto为主语称其写有关于电学机器的论著；注1列同题名及Correr定位“Misc: 105113”，并称Haskell所引本未标日期或出版者；索引子目指向同一脚注。\n"
        "- S3外部身份行 `aln-12619` 已记 Treccani DBI（Ettore Merkel, vol.45, 1995）；该条目将 *Considerazioni elettriche* 列为Maggiotto名下、威尼斯1781年出版的印刷小册子。它补足题名、作者、出版地与年份的书目身份，不能证明Haskell所引Correr副本的具体版本或当前馆藏，亦不核验其机器发明叙述。未给出版者、版次；中文题名《电学考论》为项目暂译。1882年Tessier文章 `cand-9779` 是独立书目对象；Treccani列出的另外两种1781年小册子不并入本组。\n"
        "- 新增 `units/archives/considerazioni-elettriche-1781` 卡、manifest 1条、`cand-1490` 映射和accepted路径。既有人物卡与Correr图书馆卡仅作内容入口；本轮不新增正式作者或馆藏关系，均留待S6。字段行经 `build_field_facts.py` 预检与apply登记。S4累计300组/388条映射，待登记4,539组/4,633条映射；archive为40组已登记、1,180组/1,199条成员待登记；KU总数1,319。\n"
    )

    card_text = make_card()
    frontmatter = yaml.safe_load(card_text.split("---\n", 2)[1])
    if frontmatter.get("type") != "archive" or len(frontmatter.get("sources", [])) != 4:
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
    print(f"  group={GROUP}; candidates=1; title/year=Considerazioni elettriche / Venice 1781")
    print("  S4=299/387 -> 300/388; pending=4,539/4,633; KU=1,319")
    print("  archive=39/1,181 -> 40/1,180 groups; pending candidates=1,199")
    print("  sources.csv unchanged; formal relations unchanged")
    if args.dry_run:
        print("Dry-run passed; no files changed.")
        return

    backup_targets = [ALIGNMENT, MANIFEST, ACCEPTED, PROCESS, RESULT]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in backup_targets]
    if any(path.exists() for path in backups):
        raise SystemExit("A Maggiotto S4 recovery copy already exists; inspect before applying.")
    for original, backup in zip(backup_targets, backups, strict=True):
        shutil.copy2(original, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s4-maggiotto-considerazioni-elettriche-1781-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied Maggiotto archive registration.")


if __name__ == "__main__":
    main()
