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
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md"
BACKUP_SUFFIX = ".bak-s4-henri-dorleans-duc-aumale-20261016"

KU_ID = "units/persons/henri-dorleans-duc-aumale"
CARD_REL = "04-knowledge/units/persons/henri-dorleans-duc-aumale.md"
GROUP = "person-group-henri-dorleans-duc-aumale-1822-1897"
CID = "cand-7090"
BNF_URL = "https://catalogue.bnf.fr/ark:/12148/cb12375307v"
DATE = "2026-10-16"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)


def read_csv(path: Path):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader), bom


def encode_csv(fields: list[str], rows: list[dict[str, str]], bom: bool) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    text = stream.getvalue()
    return ("\ufeff" + text if bom else text).encode("utf-8")


def encode_text(path: Path, text: str) -> bytes:
    bom = path.read_bytes().startswith(b"\xef\xbb\xbf")
    return ("\ufeff" + text if bom else text).encode("utf-8")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def group_of(note: str) -> str:
    match = re.search(r"group=([^;|\s]+)", note)
    return match.group(1) if match else ""


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected one occurrence of {old!r}, found {count}")
    return text.replace(old, new, 1)


def make_card() -> str:
    name_en = "Henri d’Orléans, duc d’Aumale"
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第21章书末参考书目；Markdown行82；责任者形式 `d’Aumale, duc`",
            "sentence_summary": (
                "Haskell书目以`d’Aumale, duc`作为1861年马萨林清单刊本的责任者形式；此处只保留书内名称用法，"
                "具体人物身份依据BnF人物权威记录对齐。"
            ),
            "original_quotes": [{"source_span": "line 82", "text": "d’Aumale, duc:"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
                "source_span": "line 82; bibliography entry for the 1861 Mazarin inventory edition",
            },
        },
        {
            "citation": f"BnF Catalogue général, notice de personne FRBNF12375307. {BNF_URL}. Accessed {DATE}.",
            "url": BNF_URL,
            "accessed_date": DATE,
            "location": "BnF authority record FRBNF12375307；standard name, ducal title, birth and death years",
            "sentence_summary": (
                "BnF Catalogue général's person authority record identifies Aumale as Henri d’Orléans, duc d’Aumale (1822–1897); "
                "used only to resolve the name form and dates, without extending the biography."
            ),
            "original_quotes": [],
        },
    ]
    frontmatter = {
        "title": f"亨利·德·奥尔良，奥马勒公爵（{name_en}，1822–1897）",
        "name_en": name_en,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": PROCESS_REF,
    }
    header = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    body = """## 内容

### 描述

**中文：** 本卡登记亨利·德·奥尔良（奥马勒公爵，1822–1897）。BnF Catalogue général人物权威记录FRBNF12375307将“Henri d’Orléans, duc d’Aumale”列为规范身份名称并给出生卒年。Haskell第21章书目在1861年马萨林清单刊本条目中使用责任者形式“d’Aumale, duc”；该形式与BnF人物记录相合。此处只保存名称、头衔、年代和书目中的责任者用名，不扩展生平。与《Inventaire de tous les meubles du Cardinal Mazarin》的正式责任关系留待S6审查；书目记录不自动构成正式关系边。

**English:** This card records Henri d’Orléans, duc d’Aumale (1822–1897). BnF Catalogue général person authority record FRBNF12375307 gives “Henri d’Orléans, duc d’Aumale” as the authorized identity form and supplies the life dates. Chapter 21 of Haskell’s bibliography uses the responsibility form “d’Aumale, duc” for the 1861 edition of the Mazarin inventory; this form matches the BnF authority record. The card records only the name, title, dates, and the bibliographic name form, without extending the biography. The formal responsibility relation to *Inventaire de tous les meubles du Cardinal Mazarin* remains for S6 review; the bibliography entry alone is not a formal relation edge.

### 身份信息

| 字段 | 内容 | 证据 |
|---|---|---|
| 规范名称 | Henri d’Orléans, duc d’Aumale | S2 |
| 头衔 | duc d’Aumale（奥马勒公爵） | S2 |
| 生卒年 | 1822–1897 | S2 |
| 书目责任形式 | Haskell书目写作“d’Aumale, duc”，对应1861年马萨林清单刊本条目 | S1；S2 |

## 关系与证据

### 关系记录

尚无正式关系记录。Haskell书目所示与1861年刊本的责任关系留待S6审核；本卡记录身份映射，不把书目归属直接写成正式边。
"""
    return f"---\n{header}---\n\n{body}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Register Henri d'Orléans, duc d'Aumale in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignment_rows, alignment_bom = read_csv(ALIGNMENT)
    manifest_fields, manifest_rows, manifest_bom = read_csv(MANIFEST)
    primary = [row for row in alignment_rows if row.get("candidate_id") == CID and not row.get("external_source")]
    external = [row for row in alignment_rows if row.get("candidate_id") == CID and row.get("external_id") == BNF_URL]
    if len(manifest_rows) != 1321 or any(row.get("ku_id") == KU_ID for row in manifest_rows):
        raise SystemExit("Unexpected S4 manifest baseline or Henri d'Orléans target already exists.")
    if len(primary) != 1 or len(external) != 1:
        raise SystemExit("Expected one primary candidate row and one BnF authority identity row for cand-7090.")
    if primary[0].get("decision") != "new" or primary[0].get("ku_id") or group_of(primary[0].get("resolution_note", "")) != GROUP:
        raise SystemExit("cand-7090 is no longer an unmapped member of its person identity group.")
    if external[0].get("decision") != "new":
        raise SystemExit("The BnF authority alignment row is no longer active.")
    members = [row["candidate_id"] for row in alignment_rows
               if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
               and group_of(row.get("resolution_note", "")) == GROUP]
    if members != [CID]:
        raise SystemExit(f"Unexpected membership of {GROUP}: {members}")
    card_path = ROOT / CARD_REL
    if card_path.exists():
        raise SystemExit(f"S4 card already exists: {CARD_REL}")

    planned_alignment = [dict(row) for row in alignment_rows]
    primary_row = next(row for row in planned_alignment if row.get("candidate_id") == CID and not row.get("external_source"))
    primary_row["ku_id"] = KU_ID
    primary_row["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest_rows)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": "亨利·德·奥尔良，奥马勒公爵",
        "name_en": "Henri d’Orléans, duc d’Aumale",
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    planned_manifest.sort(key=lambda row: row["ku_id"])

    accepted_lines = ACCEPTED.read_text(encoding="utf-8-sig").splitlines()
    if any(line.strip() == f"- {CARD_REL}" for line in accepted_lines):
        raise SystemExit("Accepted path already exists.")
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    result_text = RESULT.read_text(encoding="utf-8-sig")
    result_text = replace_once(result_text,
        "S4 已登记302组、映射393条成员候选；尚待登记4,538组、4,630条映射。",
        "S4 已登记303组、映射394条成员候选；尚待登记4,537组、4,629条映射。")
    result_text = replace_once(result_text, "1,321 KU；新组登记与待登记分类型统计见下表", "1,322 KU；新组登记与待登记分类型统计见下表")
    result_text = replace_once(result_text,
        "| person | 1,004→387 | 1,177／1,084 | 88／996；1,041 | 3 | 7 | 1,273 |",
        "| person | 1,004→387 | 1,177／1,084 | 89／995；1,040 | 3 | 7 | 1,273 |")
    result_text = replace_once(result_text,
        "| **合计** | **1,774→1,026** | **5,023／4,840** | **302／4,538；4,630** | **8** | **100** | **5,499** |",
        "| **合计** | **1,774→1,026** | **5,023／4,840** | **303／4,537；4,629** | **8** | **100** | **5,499** |")
    detail = (
        "### S4 person：Henri d’Orléans, duc d’Aumale（1822–1897）（2026-10-16）\n\n"
        "- `cand-7090`按BnF人物权威记录FRBNF12375307登记至 `units/persons/henri-dorleans-duc-aumale`。该权威记录将书目形式 `d’Aumale, duc` 识别为Henri d’Orléans, duc d’Aumale，并给出1822–1897；未扩写其他传记事实。\n"
        "- 本次新增1张person卡、manifest 1条、候选映射1条及accepted路径。其与1861年马萨林清单刊本的正式责任关系留待S6，不新增relations.csv边。S4累计303组/394条映射，待登记4,537组/4,629条映射；person为89组已登记、995组/1,040条成员待登记；KU总数1,322。字段行经 `build_field_facts.py` 预检与apply登记。\n\n"
    )
    result_text = replace_once(result_text, "## 未解决项与交接限制", detail + "## 未解决项与交接限制")

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    heading = "### S4 person：Henri d’Orléans, duc d’Aumale（1822–1897）"
    if heading in process_text:
        raise SystemExit("Henri d'Orléans S4 process record already exists.")
    process_text += (
        f"\n\n{heading}（{DATE}）\n\n"
        "- S3组 `person-group-henri-dorleans-duc-aumale-1822-1897` 仅含 `cand-7090`，来源形式为Haskell第7章注释的`d’Aumale`及第21章书目的`d’Aumale, duc`。"
        "BnF人物权威记录FRBNF12375307确认其为Henri d’Orléans, duc d’Aumale，1822–1897。\n"
        "- 新增 `units/persons/henri-dorleans-duc-aumale` 卡和manifest/accepted记录；该人物与1861年马萨林清单刊本的责任关系仍待S6审查，不创建正式边。未添加额外生平信息。\n"
        "- `build_field_facts.py` 将从卡内证据表登记字段事实及BnF权威来源；S4累计303组/394条映射，待登记4,537组/4,629条映射；person为89组已登记、995组/1,040条成员待登记；KU总数1,322。\n"
    )

    card_text = make_card()
    frontmatter = yaml.safe_load(card_text.split("---\n", 2)[1])
    if frontmatter.get("type") != "person" or len(frontmatter.get("sources", [])) != 2:
        raise SystemExit("Generated Henri d'Orléans person card frontmatter failed validation.")
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
        print(f"  {path.relative_to(ROOT)}: {digest(path.read_bytes()) if path.exists() else 'absent'} -> {digest(content)}")
    print(f"  group={GROUP}; candidates=1; card={KU_ID}")
    print("  S4=302/393 -> 303/394; pending=4,537/4,629; KU=1,322")
    print("  person=88/996 -> 89/995 groups; pending candidates=1,040")
    print("  BnF authority source will be added once by build_field_facts.py; formal relations unchanged")
    if args.dry_run:
        print("Dry-run passed; no files changed.")
        return

    backup_targets = [ALIGNMENT, MANIFEST, ACCEPTED, PROCESS, RESULT]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in backup_targets]
    if any(path.exists() for path in backups):
        raise SystemExit("A Henri d'Orléans S4 recovery copy already exists; inspect before applying.")
    for original, backup in zip(backup_targets, backups, strict=True):
        shutil.copy2(original, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s4-henri-dorleans-aumale-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied Henri d'Orléans person registration.")


if __name__ == "__main__":
    main()
